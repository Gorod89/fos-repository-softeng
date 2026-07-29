from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]


def test_architecture_has_measurable_quality_attributes() -> None:
    model = yaml.safe_load((ROOT / "architecture.yml").read_text(encoding="utf-8"))
    required = {
        "latency_p95_ms",
        "availability_percent",
        "audit_log_retention_days",
        "recovery_time_minutes",
    }
    assert required <= model["quality_attributes"].keys(), (
        "Укажите четыре измеримых атрибута качества."
    )


def test_component_ids_are_unique() -> None:
    model = yaml.safe_load((ROOT / "architecture.yml").read_text(encoding="utf-8"))
    ids = [component["id"] for component in model["components"]]
    assert len(ids) == len(set(ids)), "Идентификаторы компонентов должны быть уникальны."
