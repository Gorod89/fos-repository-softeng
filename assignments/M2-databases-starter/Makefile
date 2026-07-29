.PHONY: doctor install test check
doctor:
	@python --version
	@uv --version
	@docker compose version
install:
	uv sync --frozen
test:
	uv run pytest -q
check: test
