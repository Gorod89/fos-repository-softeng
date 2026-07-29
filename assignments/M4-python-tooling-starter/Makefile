.PHONY: doctor install test lint check
doctor:
	@python --version
	@uv --version
install:
	uv sync --frozen
test:
	uv run pytest -q
lint:
	uv run ruff check src tests
check: lint test
