from pathlib import Path

from scripts.validate_course import (
    validate_assessment,
    validate_datasets,
    validate_learning_outcomes,
    validate_rubrics,
)

ROOT = Path(__file__).parents[2]


def test_assessment_model_is_consistent() -> None:
    assert validate_assessment(ROOT) == []


def test_rubrics_and_learning_outcomes_are_traceable() -> None:
    issues, kim_ids, lo_refs = validate_rubrics(ROOT)
    assert issues == []
    assert validate_learning_outcomes(ROOT, kim_ids, lo_refs) == []


def test_dataset_checksums_match() -> None:
    assert validate_datasets(ROOT) == []
