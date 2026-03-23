# Technology Stack: Grocery Purchase History Scraper

## Language
- **Python (3.12):** The core language for development, leveraging its rich ecosystem for scraping, data manipulation, and testing.

## Scraping & Automation
- **Playwright:** Provides powerful browser automation for navigating the Kroger website and handling complex interactions like login.
- **BeautifulSoup (bs4):** Efficiently parses HTML from the receipt pages to extract structured purchase data.
- **fake-useragent:** Assists in evading bot detection by rotating and mimicking real user-agent strings.

## Configuration & Data Validation
- **Pydantic (v2):** Ensures that all parsed data (receipts, items, stores) conforms to a strict schema.
- **Pydantic Settings:** Manages application configuration via environment variables with strong typing and validation.

## Quality Assurance & Testing
- **Pytest:** The primary framework for writing and running the test suite.
- **Pytest-Playwright:** Simplifies the use of Playwright within the test environment.
- **Pytest-Cov:** Generates coverage reports to ensure high test coverage.
- **Flake8:** Enforces consistent code style and identifies potential issues.
- **Mypy:** Provides static type checking for improved code safety and reliability.

## Infrastructure & Tooling
- **Docker & Docker Compose:** Containerizes the application for consistent execution across different environments.
- **Makefile:** Provides a unified interface for common development tasks (lint, test, run).
- **pre-commit:** Automates code quality checks before each commit.
