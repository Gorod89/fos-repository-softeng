.PHONY: install validate test docs serve

install:
	uv sync --frozen

validate:
	uv run python scripts/validate_course.py

test:
	uv run pytest

docs:
	uv run mkdocs build --strict

serve:
	uv run mkdocs serve
