default: help

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[\/a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' Makefile

requirements: ## Install requirements
	pip install -r requirements.txt

test: ## build container locally
	pytest .

lint: ## run pycodestyle on python files
	pycodestyle

check_browser: ## Check to see if browser settings pass bot checks
	python src/util/test_browser_settings.py

