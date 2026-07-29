from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def check(repo: Path) -> list[str]:
    errors: list[str] = []
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout
    if status:
        errors.append("Рабочее дерево должно быть чистым.")
    test = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, capture_output=True)
    if test.returncode:
        errors.append("Тест, используемый для bisect, все еще падает.")
    return errors


if __name__ == "__main__":
    problems = check(Path(sys.argv[1] if len(sys.argv) > 1 else "workspace"))
    print("\n".join(problems) if problems else "Публичная проверка пройдена.")
    raise SystemExit(bool(problems))
