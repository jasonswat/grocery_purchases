default: help

PYTHONPATH := ./src
LOGLEVEL ?= INFO
export PYTHONPATH LOGLEVEL

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[\/a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' Makefile

setup: ## Setup virtual environment and install requirements
	uv sync

lint: ## run pycodestyle on python files
	uv run flake8 ./src
	uv run mypy --ignore-missing-imports --check-untyped-defs ./src

test: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html

coverage: ## Run tests with coverage and display report in terminal
	uv run pytest --cov=src --cov-report=term-missing

check_browser: ## Check to see if browser settings pass bot checks
	uv run python src/util/helper_browser_settings.py

test_get_receipts:  ## Run get_receipts function with sample data
	MAX_SLEEP=3 uv run python src/util/helper_get_receipts.py

main:  ## Run main.py 
	PYTHONPATH=./src uv run python src/main.py

docker-build: ## Build the docker image
	docker build -t grocery-purchases .

docker-run: ## Run the docker container
	docker compose up --build

docker-test: ## Run tests inside the docker container
	docker run --rm grocery-purchases uv run pytest tests
