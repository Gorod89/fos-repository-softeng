.PHONY: doctor install test run check
doctor:
	@python --version
	@uv --version
install:
	uv sync --frozen
test:
	uv run pytest -q
run:
	PYTHONPATH=src uv run uvicorn m7_api.main:app --reload
check: test
