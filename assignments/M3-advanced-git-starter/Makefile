.PHONY: doctor install test check scenario
doctor:
	@python --version
	@git --version
	@uv --version
install:
	uv sync --frozen
scenario:
	uv run python create_scenario.py workspace
test:
	uv run pytest -q
check: test
