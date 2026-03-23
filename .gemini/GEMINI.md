# Gemini Project Guide: Kroger Grocery Scraper

This document provides instructions and context for working on this project with the Gemini CLI.

## Project Overview

This project is a Python-based web scraper designed to pull grocery purchase data from the Kroger website. It uses customer authentication to access purchase history and saves the data as partitioned JSON files in the `output/receipts/` directory.

The ultimate goal of this project is to use the collected data to power an intelligent assistant that can:
-   Generate grocery lists.
-   Predict best pricing for items.
-   Assist with household budgeting.

### Data Model
The scraper extracts and saves the following fields for each receipt:
- `receipt_id`, `date`, `total`, `tax`
- `store_name`, `store_id` (Banner and Store Number)
- `order_type` (In-Store, Pickup, or Delivery)
- `items` (List of products with UPC, price, quantity, and weight)

## Development

### Language and Style

-   **Language:** Python
-   **Style Guide:** All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).
-   **Linting:** This project uses `flake8` for linting. Please ensure all new or modified code passes the linter. Refer to the `.flake8` configuration file for any project-specific rule adjustments.

### Key Dependencies

- **Scraping:** The project uses Playwright for browser automation to handle the login process and navigate the Kroger website.
- **Parsing:** BeautifulSoup is used to parse HTML content from the receipt pages.

### Running the Application

- Use the `Makefile` for common development tasks.
- `make lint`: Run the linter.
- `make test`: Run the test suite.
- `make main`: Run the main application.

## Deployment

The application is designed to be deployed as a containerized service.

-   **Containerization:** A `Dockerfile` is used to build the application into a container image.
-   **Deployment Platform:** The container is deployed as a serverless job on Google Cloud Run.
