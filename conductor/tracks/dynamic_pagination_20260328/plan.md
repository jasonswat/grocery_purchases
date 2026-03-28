# Implementation Plan: Dynamic Pagination for Purchase History

## Phase 1: Research and Specification
- [x] Task: Review current `src/main.py` CLI logic and identify where to insert the new `--pages` argument.
- [x] Task: Analyze `src/util/helper_get_receipts.py` and `src/kroger.py` to identify the URL generation logic and how it can be modified to accept a `page_num`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Research and Specification' (Protocol in workflow.md)

## Phase 2: Test Infrastructure
- [x] Task: Create a directory `tests/html/pagination/` and populate it with multiple sample purchase history files (`p1.html`, `p2.html`).
- [x] Task: Update the test setup to allow pointing to this local directory for pagination tests.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Test Infrastructure' (Protocol in workflow.md)

## Phase 3: Implementation (TDD)
- [x] Task: **Update CLI Arguments:** Modify `src/main.py` to accept the `--pages` argument and parse its values (`all`, `maxN`, `N`).
    - [x] Write unit tests for the new CLI argument parsing logic.
    - [x] Implement the parsing in `src/main.py`.
- [x] Task: **Refactor URL Generation:** Update `src/util/helper_get_receipts.py` to include a dynamic URL generator for both local and live modes.
    - [x] Write tests for the `get_purchase_url(page_num)` function (testing both `file://` and `https://` schemes).
    - [x] Implement `get_purchase_url(page_num)`.
- [x] Task: **Implement Pagination Logic:** Update the scraping loop in `src/kroger.py` (or relevant helper) to handle multiple pages based on the `--pages` argument.
    - [x] Write integration tests for `--pages=N`, `--pages=maxN`, and `--pages=all` modes.
    - [x] Implement the pagination loop in the scraper.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Implementation (TDD)' (Protocol in workflow.md)

## Phase 4: Verification and Finalization
- [x] Task: Run the full test suite (`make test`) and ensure all tests pass.
- [x] Task: Verify that test coverage is at least 80% (`make coverage`).
- [x] Task: Manually verify the new pagination logic by scraping from the local test files.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Verification and Finalization' (Protocol in workflow.md)
