# Implementation Plan: Dynamic Pagination for Purchase History

## Phase 1: Research and Specification
- [ ] Task: Review current `src/main.py` CLI logic and identify where to insert the new `--pages` argument.
- [ ] Task: Analyze `src/util/helper_get_receipts.py` and `src/kroger.py` to identify the URL generation logic and how it can be modified to accept a `page_num`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Research and Specification' (Protocol in workflow.md)

## Phase 2: Test Infrastructure
- [ ] Task: Create a directory `tests/html/pagination/` and populate it with multiple sample purchase history files (`p1.html`, `p2.html`).
- [ ] Task: Update the test setup to allow pointing to this local directory for pagination tests.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Test Infrastructure' (Protocol in workflow.md)

## Phase 3: Implementation (TDD)
- [ ] Task: **Update CLI Arguments:** Modify `src/main.py` to accept the `--pages` argument and parse its values (`all`, `maxN`, `N`).
    - [ ] Write unit tests for the new CLI argument parsing logic.
    - [ ] Implement the parsing in `src/main.py`.
- [ ] Task: **Refactor URL Generation:** Update `src/util/helper_get_receipts.py` to include a dynamic URL generator for both local and live modes.
    - [ ] Write tests for the `get_purchase_url(page_num)` function (testing both `file://` and `https://` schemes).
    - [ ] Implement `get_purchase_url(page_num)`.
- [ ] Task: **Implement Pagination Logic:** Update the scraping loop in `src/kroger.py` (or relevant helper) to handle multiple pages based on the `--pages` argument.
    - [ ] Write integration tests for `--pages=N`, `--pages=maxN`, and `--pages=all` modes.
    - [ ] Implement the pagination loop in the scraper.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Implementation (TDD)' (Protocol in workflow.md)

## Phase 4: Verification and Finalization
- [ ] Task: Run the full test suite (`make test`) and ensure all tests pass.
- [ ] Task: Verify that test coverage is at least 80% (`make coverage`).
- [ ] Task: Manually verify the new pagination logic by scraping from the local test files.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Verification and Finalization' (Protocol in workflow.md)
