from pathlib import Path

from scripts.validate_course import (
    validate_content,
    validate_markdown_links,
    validate_security_baseline,
    validate_starters,
)

ROOT = Path(__file__).parents[2]


def test_internal_markdown_links_work() -> None:
    assert validate_markdown_links(ROOT) == []


def test_eight_starters_follow_the_contract() -> None:
    assert validate_starters(ROOT) == []


def test_published_content_has_no_placeholders() -> None:
    assert validate_content(ROOT) == []


def test_security_baseline_is_present() -> None:
    assert validate_security_baseline(ROOT) == []
