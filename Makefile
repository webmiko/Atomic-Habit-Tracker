.PHONY: install lint format typecheck test check run

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

test:
	poetry run pytest --cov=src --cov-report=term-missing

check: lint format typecheck test

run:
	poetry run python main.py
