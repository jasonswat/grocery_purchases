default: help

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[\/a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' Makefile

requirements: ## Install requirements
	pip install -r requirements.txt

test: ## build container locally
	PYTHONPATH=./src pytest .

test-coverage: ## Run tests with coverage
	PYTHONPATH=./src pytest --cov=src --cov-report=html

lint: ## run pycodestyle on python files
	flake8 ./src	

check_browser: ## Check to see if browser settings pass bot checks
	PYTHONPATH=./src python src/util/helper_browser_settings.py

test_get_receipts:  ## Run get_receipts function with sample data
	PYTHONPATH=./src python src/util/helper_get_receipts.py

