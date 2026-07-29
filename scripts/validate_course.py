from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")


@dataclass(frozen=True)
class Issue:
    path: Path
    code: str
    message: str

    def render(self, root: Path) -> str:
        return f"{self.path.relative_to(root)}: {self.code}: {self.message}"


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("корневое значение YAML должно быть отображением")
    return value


def validate_assessment(root: Path) -> list[Issue]:
    path = root / "course-spec/assessment-model.yml"
    model = load_yaml(path)
    issues: list[Issue] = []
    total = sum(component.get("max_score", 0) for component in model.get("components", []))
    if total != model.get("maximum_score") or total != 100:
        issues.append(Issue(path, "ASSESSMENT_TOTAL", f"сумма компонентов {total}, ожидается 100"))
    if model.get("attestation") != "зачет":
        issues.append(Issue(path, "ATTESTATION", "форма аттестации должна быть «зачет»"))
    decision = model.get("decision", {})
    if {decision.get("passed"), decision.get("failed")} != {"Зачтено", "Не зачтено"}:
        issues.append(Issue(path, "ATTESTATION_SCALE", "для зачета нужна бинарная шкала"))
    if model.get("pass_score") != 60:
        issues.append(Issue(path, "PASS_SCORE", "порог зачета должен быть равен 60"))
    for component in model.get("components", []):
        for reference in component.get("rubric_refs", []):
            if not (root / "course-spec" / reference).is_file():
                issues.append(Issue(path, "RUBRIC_REF", f"не найдена рубрика {reference}"))
    return issues


def validate_rubrics(root: Path) -> tuple[list[Issue], set[str], set[str]]:
    issues: list[Issue] = []
    criterion_ids: set[str] = set()
    kim_ids: set[str] = set()
    lo_refs: set[str] = set()
    for path in sorted((root / "course-spec/rubrics").glob("*.yml")):
        rubric = load_yaml(path)
        if rubric.get("schema_version") != 1:
            issues.append(Issue(path, "SCHEMA_VERSION", "ожидается schema_version: 1"))
        kim = rubric.get("kim")
        if not isinstance(kim, str) or kim in kim_ids:
            issues.append(Issue(path, "KIM_ID", f"неуникальный или пустой ID КИМ: {kim!r}"))
        else:
            kim_ids.add(kim)
        refs = rubric.get("learning_outcome_refs", [])
        if not refs:
            issues.append(Issue(path, "LO_REFS", "рубрика не связана с результатом обучения"))
        lo_refs.update(refs)
        criteria = rubric.get("criteria", [])
        score = sum(criterion.get("score", 0) for criterion in criteria)
        expected = rubric.get("raw_max_score", rubric.get("max_score"))
        if score != expected:
            issues.append(
                Issue(path, "RUBRIC_TOTAL", f"сумма критериев {score}, ожидается {expected}")
            )
        if "raw_max_score" in rubric:
            converted = rubric["raw_max_score"] * rubric.get("conversion_factor", 0)
            if converted != rubric.get("max_score"):
                issues.append(
                    Issue(path, "RUBRIC_SCALE", "коэффициент не переводит сырую шкалу в max_score")
                )
        for criterion in criteria:
            criterion_id = criterion.get("id")
            if not isinstance(criterion_id, str) or criterion_id in criterion_ids:
                issues.append(
                    Issue(path, "CRITERION_ID", f"неуникальный критерий {criterion_id!r}")
                )
            else:
                criterion_ids.add(criterion_id)
            if not criterion.get("evidence"):
                issues.append(
                    Issue(path, "EVIDENCE", f"для {criterion_id!r} не указано свидетельство")
                )
    return issues, kim_ids, lo_refs


def validate_learning_outcomes(
    root: Path, kim_ids: set[str], rubric_lo_refs: set[str]
) -> list[Issue]:
    path = root / "course-spec/learning-outcomes.yml"
    model = load_yaml(path)
    issues: list[Issue] = []
    seen: set[str] = set()
    for outcome in model.get("learning_outcomes", []):
        outcome_id = outcome.get("id")
        if not isinstance(outcome_id, str) or outcome_id in seen:
            issues.append(Issue(path, "LO_ID", f"неуникальный результат {outcome_id!r}"))
            continue
        seen.add(outcome_id)
        if outcome_id not in rubric_lo_refs:
            issues.append(Issue(path, "LO_RUBRIC", f"{outcome_id} не связан с рубрикой"))
        evidence = set(outcome.get("evidence", []))
        missing = evidence - kim_ids
        if missing:
            issues.append(
                Issue(path, "LO_EVIDENCE", f"{outcome_id}: неизвестные КИМ {sorted(missing)}")
            )
    unknown_refs = rubric_lo_refs - seen
    if unknown_refs:
        issues.append(Issue(path, "LO_REF", f"рубрики ссылаются на {sorted(unknown_refs)}"))
    return issues


def validate_datasets(root: Path) -> list[Issue]:
    path = root / "course-spec/datasets.yml"
    model = load_yaml(path)
    issues: list[Issue] = []
    for dataset in model.get("datasets", []):
        data_path = root / dataset["path"]
        if not data_path.is_file():
            issues.append(Issue(path, "DATASET_PATH", f"не найден {dataset['path']}"))
            continue
        digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if digest != dataset.get("sha256"):
            issues.append(
                Issue(
                    path,
                    "DATASET_SHA256",
                    f"{dataset['id']}: {digest} не совпадает со спецификацией",
                )
            )
    return issues


def normalize_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " \"" in target:
        target = target.split(" \"", 1)[0]
    return unquote(target.split("#", 1)[0])


def validate_markdown_links(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    excluded = {".git", ".venv", "site"}
    for path in root.rglob("*.md"):
        if excluded.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = normalize_link_target(raw)
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                issues.append(Issue(path, "LINK_ESCAPE", f"ссылка выходит за репозиторий: {raw}"))
                continue
            if not resolved.exists():
                issues.append(Issue(path, "BROKEN_LINK", f"не найдено: {raw}"))
    return issues


def validate_starters(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    assignments = root / "assignments"
    starters = sorted(assignments.glob("M*-starter"))
    if len(starters) != 8:
        issues.append(Issue(assignments, "STARTER_COUNT", f"найдено {len(starters)}, ожидается 8"))
    required = {"README.md", "AI_USAGE.md", "pyproject.toml", "uv.lock", "Makefile"}
    for starter in starters:
        missing = sorted(name for name in required if not (starter / name).is_file())
        if missing:
            issues.append(Issue(starter, "STARTER_CONTRACT", f"нет файлов {missing}"))
        if not list((starter / "tests/public").glob("test_*.py")):
            issues.append(Issue(starter, "PUBLIC_TESTS", "нет публичных тестов"))
        makefile = starter / "Makefile"
        if makefile.is_file():
            content = makefile.read_text(encoding="utf-8")
            for command in ("doctor:", "install:", "test:", "check:"):
                if command not in content:
                    issues.append(Issue(makefile, "MAKE_TARGET", f"нет цели {command[:-1]}"))
    return issues


def validate_content(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    expected_title = load_yaml(root / "course-spec/metadata.yml")["course"]["title"]
    for relative in ("README.md", "docs/rpd.md"):
        path = root / relative
        if expected_title not in path.read_text(encoding="utf-8"):
            issues.append(Issue(path, "COURSE_TITLE", "название не совпадает с metadata.yml"))
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or path.suffix not in {".md", ".yml", ".yaml"}
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if "[ЗАПОЛНИТЬ]" in text:
            issues.append(Issue(path, "PLACEHOLDER", "остался маркер [ЗАПОЛНИТЬ]"))
    critical = "\n".join(
        (root / relative).read_text(encoding="utf-8")
        for relative in ("README.md", "docs/rpd.md", "course-spec/metadata.yml")
    )
    for pattern, message in (
        (r"\bGithub\b", "используйте GitHub"),
        (r"\bСI/CD\b", "в CI/CD смешаны алфавиты"),
        (r"\(\s*C\s*\)", "уровень C должен быть кириллическим С"),
    ):
        if re.search(pattern, critical):
            issues.append(Issue(root / "docs/rpd.md", "TERMINOLOGY", message))
    return issues


def validate_security_baseline(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    ignore = (root / ".gitignore").read_text(encoding="utf-8")
    for pattern in (".env", "*.pem", "site/", ".pytest_cache/", ".ruff_cache/"):
        if pattern not in ignore:
            issues.append(Issue(root / ".gitignore", "GITIGNORE", f"нет правила {pattern}"))
    for workflow in (root / ".github/workflows").glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        if "pull_request_target:" in text:
            issues.append(Issue(workflow, "UNSAFE_TRIGGER", "pull_request_target запрещен"))
        if "permissions:" not in text:
            issues.append(Issue(workflow, "PERMISSIONS", "права workflow не заданы"))
        for action_ref in re.findall(r"^\s*uses:\s+[^@\s]+@([^\s#]+)", text, flags=re.MULTILINE):
            if not re.fullmatch(r"[0-9a-f]{40}", action_ref):
                issues.append(
                    Issue(
                        workflow,
                        "ACTION_PIN",
                        f"GitHub Action должен быть закреплен полным SHA: {action_ref}",
                    )
                )
    return issues


def validate(root: Path = ROOT) -> list[Issue]:
    issues = validate_assessment(root)
    rubric_issues, kim_ids, rubric_lo_refs = validate_rubrics(root)
    issues.extend(rubric_issues)
    issues.extend(validate_learning_outcomes(root, kim_ids, rubric_lo_refs))
    issues.extend(validate_datasets(root))
    issues.extend(validate_markdown_links(root))
    issues.extend(validate_starters(root))
    issues.extend(validate_content(root))
    issues.extend(validate_security_baseline(root))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))


def main() -> int:
    issues = validate(ROOT)
    if issues:
        for issue in issues:
            print(issue.render(ROOT))
        print(f"\nПроверка не пройдена: проблем — {len(issues)}.")
        return 1
    print("Проверка пройдена: модель курса, ссылки, данные и starter-проекты согласованы.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
