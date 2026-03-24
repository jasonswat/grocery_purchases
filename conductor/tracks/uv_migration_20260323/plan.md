# Implementation Plan: Replace pyenv with uv for Python Environment and Docker

## Phase 1: Local Environment Migration
- [x] Task: Initialize `uv` in the project.
    - [x] Run `uv init` (if not already done) or configure `pyproject.toml` for `uv`.
    - [x] Create `uv.lock` using `uv sync`.
    - [x] Pin the Python version to 3.12 in `pyproject.toml`.
- [x] Task: Update local development workflow.
    - [x] Verify `uv run` for executing the application and tests.
    - [x] Update documentation (README.md) to explain the new `uv` setup.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Local Environment Migration' (Protocol in workflow.md)

## Phase 2: Tooling and Task Automation
- [x] Task: Update the `Makefile`.
    - [x] Refactor `make lint`, `make test`, and `make main` to use `uv run`.
    - [x] Add `make setup` using `uv sync`.
- [x] Task: Update CI/CD and pre-commit hooks.
    - [x] Update `.pre-commit-config.yaml` if it relies on a specific Python environment.
- [x] Task: Clean up legacy environment files.
    - [x] Remove `requirements.txt`.
    - [x] (Optional) Remove `.python-version` if it's strictly for `pyenv`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Tooling and Task Automation' (Protocol in workflow.md)

## Phase 3: Docker Integration
- [x] Task: Refactor the `Dockerfile`.
    - [x] Install `uv` in the base or build stage.
    - [x] Copy `pyproject.toml` and `uv.lock` early to leverage layer caching.
    - [x] Use `uv sync` to install dependencies into a dedicated environment.
    - [x] Update the `ENTRYPOINT` or `CMD` to run via `uv run` if necessary.
- [x] Task: Verify Docker build and execution.
    - [x] Build the container locally and ensure it starts and runs correctly.
    - [x] Check final image size and optimize if needed.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Docker Integration' (Protocol in workflow.md)

## Phase 4: Finalization and Documentation
- [x] Task: Update Conductor project files.
    - [x] Update `conductor/tech-stack.md` to reflect the move to `uv`.
- [x] Task: Final project review.
    - [x] Ensure all tests pass across all environments (local, Docker).
    - [x] Verify the complete removal of `pyenv` dependencies.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Finalization and Documentation' (Protocol in workflow.md)
