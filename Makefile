.DEFAULT_GOAL := help
PYTHONPATH = ./
TEST = pytest --verbosity=2 --showlocals --log-level=DEBUG --strict-markers $(arg)
APPMODULE = app.main:app $(arg)
CODE = app tests

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Runs pytest with coverage
	$(TEST) --cov

.PHONY: test-fast
test-fast: ## Runs pytest with exitfirst
	$(TEST) --exitfirst

.PHONY: test-failed
test-failed: ## Runs pytest from last-failed
	$(TEST) --last-failed

.PHONY: test-cov
test-cov: ## Runs pytest with coverage report
	$(TEST) --cov --cov-report html

.PHONY: build-env
build-env:
	poetry lock
	poetry check

.PHONY: lint
lint: ## Lint code
	black --check $(CODE)
	flake8 --jobs 4 --statistics --show-source $(CODE)
	pylint $(CODE)
	mypy $(CODE)
	pytest --dead-fixtures --dup-fixtures
	safety check --full-report
	bandit -c pyproject.toml -r $(CODE)
	poetry check

.PHONY: format
format: ## Formats all files
	autoflake --recursive --in-place --ignore-init-module-imports --remove-all-unused-imports $(CODE)
	isort $(CODE)
	black $(CODE)

.PHONY: check
check: format lint test ## Format and lint code then run tests

.PHONY: run-fast
run-fast: ## Run the app using uvicorn without dependency checks
	uvicorn $(APPMODULE) --reload

.PHONY: run
run: build-env run-fast ## Refresh the dependencies and run the app using uvicorn

.PHONY: boot
boot: build-env check run-fast
