import pandas as pd
import pytest

from m6_eda import quality_summary, survival_by_class


def sample() -> pd.DataFrame:
    return pd.DataFrame(
        {"PassengerId": [1, 2, 3], "Pclass": [1, 1, 3], "Survived": [1, 0, 0]}
    )


def test_survival_rate_is_grouped_by_class() -> None:
    assert survival_by_class(sample()).to_dict() == {1: 0.5, 3: 0.0}


def test_missing_required_column_is_explained() -> None:
    with pytest.raises(ValueError, match="Survived"):
        quality_summary(sample().drop(columns=["Survived"]))
