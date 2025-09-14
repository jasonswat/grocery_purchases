default: help

PYTHONPATH := ./src
LOGLEVEL ?= INFO
export PYTHONPATH LOGLEVEL

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[\/a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' Makefile

requirements: ## Install requirements
	pip install -r requirements.txt

lint: ## run pycodestyle on python files
	flake8 ./src
	mypy --ignore-missing-imports --check-untyped-defs ./src

test: ## Run tests with coverage
	pytest --cov=src --cov-report=html

coverage: ## Run tests with coverage and display report in terminal
	pytest --cov=src --cov-report=term-missing

check_browser: ## Check to see if browser settings pass bot checks
	python src/util/helper_browser_settings.py

test_get_receipts:  ## Run get_receipts function with sample data
	LOGLEVEL=DEBUG MAX_SLEEP=3 python src/util/helper_get_receipts.py

main:  ## Run main.py 
	PYTHONPATH=./src python src/main.py
