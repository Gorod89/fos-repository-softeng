from m2_etl.etl import UPSERT_SQL, prepare_records


def test_prepare_records_handles_missing_age() -> None:
    rows = [{"PassengerId": "1", "Pclass": "3", "Survived": "0", "Age": ""}]
    assert prepare_records(rows) == [(1, 3, False, None)]


def test_insert_is_idempotent_by_contract() -> None:
    assert "ON CONFLICT" in UPSERT_SQL.upper(), "Загрузка должна быть идемпотентной."
