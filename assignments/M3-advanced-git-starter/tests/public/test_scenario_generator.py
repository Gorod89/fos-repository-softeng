import subprocess
from pathlib import Path

from create_scenario import create_scenario


def test_generator_creates_branches_and_regression(tmp_path: Path) -> None:
    repo = tmp_path / "scenario"
    create_scenario(repo)
    branches = subprocess.run(
        ["git", "branch", "--format=%(refname:short)"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert {"main", "known-good", "feature/discount"} <= set(branches)
    test = subprocess.run(["python", "-m", "pytest", "-q"], cwd=repo, capture_output=True)
    assert test.returncode != 0, "Сценарий должен содержать детерминированную регрессию."
