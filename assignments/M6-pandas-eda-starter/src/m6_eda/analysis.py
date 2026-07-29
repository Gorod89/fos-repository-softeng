from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {"PassengerId", "Pclass", "Survived"}


def quality_summary(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Отсутствуют обязательные столбцы: {sorted(missing)}")
    return pd.DataFrame(
        {
            "missing": frame.isna().sum(),
            "distinct": frame.nunique(dropna=True),
        }
    )


def survival_by_class(frame: pd.DataFrame) -> pd.Series:
    quality_summary(frame)
    return frame.groupby("Pclass", sort=True)["Survived"].mean()
