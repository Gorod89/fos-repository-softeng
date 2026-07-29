.PHONY: doctor install test image check
doctor:
	@python --version
	@uv --version
	@docker compose version
install:
	uv sync --frozen
test:
	uv run pytest -q
image:
	docker build -t m8-course:local .
check: test image
