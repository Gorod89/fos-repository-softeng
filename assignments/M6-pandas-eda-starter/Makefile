.PHONY: doctor install test check
doctor:
	@python --version
	@uv --version
install:
	uv sync --frozen
test:
	MPLBACKEND=Agg uv run pytest -q
check: test
