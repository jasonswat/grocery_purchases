# Specification: Dynamic Pagination for Purchase History

## Overview
This track aims to make the grocery purchase history scraping process more flexible by supporting dynamic pagination. The system will handle multiple pages (or specific ranges) whether running against the live Kroger/QFC website or local HTML files.

## Functional Requirements
- **Automatic Mode Detection:** The application will automatically switch between "local" and "live" modes by examining the URL scheme (`file://` vs `https://`).
- **Dynamic Pagination CLI:** A new `--pages` argument will be added to `src/main.py`:
    - `--pages=N` (e.g., `--pages=1`): Scrapes only the specified page. Defaults to 1.
    - `--pages=all`: Scrapes all available pages until no more data is found.
    - `--pages=maxN` (e.g., `--pages=max10`): Scrapes up to the $N$ most recent pages.
- **Local File Support:**
    - Local mode will look for files in a structured directory (e.g., `tests/html/`).
    - Files will be named following a convention like `p1.html`, `p2.html` to represent different pages of the purchase history.
- **Backend Updates:** Refactor `src/util/helper_get_receipts.py` and `src/kroger.py` to accept page parameters and generate the correct URLs/file paths.

## Acceptance Criteria
- `uv run src/main.py --pages=all` successfully iterates through and parses all available purchase history pages.
- `uv run src/main.py --pages=max5` successfully scrapes the first 5 pages.
- Local mode correctly loads and parses `p1.html`, `p2.html`, etc., from the test data directory when a local path is provided.
- Unit and integration tests cover the new pagination logic and CLI arguments.

## Out of Scope
- Scraping history from other grocery banners not already supported (unless required for testing).
- Implementation of a GUI for page selection.
