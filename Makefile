.PHONY: install lint format typecheck test check run migrate

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

test:
	poetry run pytest --cov=config --cov=users --cov=habits --cov-report=term-missing

check: lint format typecheck test

run:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py migrate
