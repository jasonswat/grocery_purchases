# Implementation Plan: Replace pyenv with uv for Python Environment and Docker

## Phase 1: Local Environment Migration
- [ ] Task: Initialize `uv` in the project.
    - [ ] Run `uv init` (if not already done) or configure `pyproject.toml` for `uv`.
    - [ ] Create `uv.lock` using `uv sync`.
    - [ ] Pin the Python version to 3.12 in `pyproject.toml`.
- [ ] Task: Update local development workflow.
    - [ ] Verify `uv run` for executing the application and tests.
    - [ ] Update documentation (README.md) to explain the new `uv` setup.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Local Environment Migration' (Protocol in workflow.md)

## Phase 2: Tooling and Task Automation
- [ ] Task: Update the `Makefile`.
    - [ ] Refactor `make lint`, `make test`, and `make main` to use `uv run`.
    - [ ] Add `make setup` using `uv sync`.
- [ ] Task: Update CI/CD and pre-commit hooks.
    - [ ] Update `.pre-commit-config.yaml` if it relies on a specific Python environment.
- [ ] Task: Clean up legacy environment files.
    - [ ] Remove `requirements.txt`.
    - [ ] (Optional) Remove `.python-version` if it's strictly for `pyenv`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Tooling and Task Automation' (Protocol in workflow.md)

## Phase 3: Docker Integration
- [ ] Task: Refactor the `Dockerfile`.
    - [ ] Install `uv` in the base or build stage.
    - [ ] Copy `pyproject.toml` and `uv.lock` early to leverage layer caching.
    - [ ] Use `uv sync` to install dependencies into a dedicated environment.
    - [ ] Update the `ENTRYPOINT` or `CMD` to run via `uv run` if necessary.
- [ ] Task: Verify Docker build and execution.
    - [ ] Build the container locally and ensure it starts and runs correctly.
    - [ ] Check final image size and optimize if needed.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Docker Integration' (Protocol in workflow.md)

## Phase 4: Finalization and Documentation
- [ ] Task: Update Conductor project files.
    - [ ] Update `conductor/tech-stack.md` to reflect the move to `uv`.
- [ ] Task: Final project review.
    - [ ] Ensure all tests pass across all environments (local, Docker).
    - [ ] Verify the complete removal of `pyenv` dependencies.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Finalization and Documentation' (Protocol in workflow.md)
