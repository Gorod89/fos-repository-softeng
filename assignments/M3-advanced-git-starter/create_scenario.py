from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)


def commit(repo: Path, message: str, ordinal: int) -> None:
    env = os.environ.copy()
    date = f"2026-01-{ordinal:02d}T12:00:00+00:00"
    env.update(
        {
            "GIT_AUTHOR_NAME": "Course Bot",
            "GIT_AUTHOR_EMAIL": "course@example.invalid",
            "GIT_COMMITTER_NAME": "Course Bot",
            "GIT_COMMITTER_EMAIL": "course@example.invalid",
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
    )
    git(repo, "add", ".", env=env)
    git(repo, "commit", "-m", message, env=env)


def create_scenario(target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"{target} уже существует; данные не перезаписаны.")
    target.mkdir(parents=True)
    git(target, "init", "-b", "main")
    (target / "calculator.py").write_text("def total(values):\n    return sum(values)\n", encoding="utf-8")
    (target / "test_calculator.py").write_text(
        "from calculator import total\n\ndef test_total():\n    assert total([1, 2]) == 3\n",
        encoding="utf-8",
    )
    commit(target, "feat: добавить корректный расчет", 1)
    git(target, "branch", "known-good")
    (target / "calculator.py").write_text(
        "def total(values):\n    return sum(values) + 1  # регрессия для bisect\n",
        encoding="utf-8",
    )
    commit(target, "refactor: изменить расчет", 2)
    (target / "README.md").write_text("# Учебный калькулятор\n", encoding="utf-8")
    commit(target, "docs: добавить описание", 3)
    git(target, "switch", "-c", "feature/discount", "known-good")
    (target / "discount.py").write_text(
        "def apply_discount(value, percent):\n    return value * (1 - percent / 100)\n",
        encoding="utf-8",
    )
    commit(target, "feat: добавить скидку", 4)
    git(target, "switch", "main")


if __name__ == "__main__":
    create_scenario(Path(sys.argv[1] if len(sys.argv) > 1 else "workspace").resolve())
