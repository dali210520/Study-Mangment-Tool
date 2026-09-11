.PHONY: help install migrate makemigrations createsuperuser runserver check test test-coverage test-auth test-registration test-login test-models clean

help:
	@echo "Study Management Tool - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install all dependencies"
	@echo "  make migrate          - Run database migrations"
	@echo "  make createsuperuser  - Create a superuser for admin"
	@echo ""
	@echo "Development:"
	@echo "  make runserver        - Start development server"
	@echo "  make check            - Run Django system checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo "  make test-auth        - Run only authentication tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Remove cache and compiled files"
	@echo "  make makemigrations   - Create new migrations"

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

runserver:
	python manage.py runserver

check:
	python manage.py check

test:
	pytest

test-coverage:
	pytest --cov=apps --cov-report=html --cov-report=term-missing

test-auth:
	pytest -m authentication -v

test-registration:
	pytest tests/test_registration.py -v

test-login:
	pytest tests/test_login.py -v

test-models:
	pytest tests/test_models.py -v

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	rm -rf htmlcov/
	rm -rf .coverage
