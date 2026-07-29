from collections.abc import Iterable, Mapping


def prepare_records(rows: Iterable[Mapping[str, str]]) -> list[tuple[int, int, bool, float | None]]:
    """Преобразовать CSV-строки в записи для параметризованного INSERT."""
    result: list[tuple[int, int, bool, float | None]] = []
    for row in rows:
        age_text = row["Age"].strip()
        result.append(
            (
                int(row["PassengerId"]),
                int(row["Pclass"]),
                row["Survived"] == "1",
                float(age_text) if age_text else None,
            )
        )
    return result


UPSERT_SQL = """
INSERT INTO passengers (passenger_id, passenger_class, survived, age)
VALUES (%s, %s, %s, %s)
ON CONFLICT (passenger_id) DO UPDATE SET
  passenger_class = EXCLUDED.passenger_class,
  survived = EXCLUDED.survived,
  age = EXCLUDED.age
"""
