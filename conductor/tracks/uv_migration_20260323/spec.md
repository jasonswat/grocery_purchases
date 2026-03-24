# Specification: Replace pyenv with uv for Python Environment and Docker

## Overview
This track involves migrating the Python environment and dependency management from `pyenv` to `uv`. This change will streamline local development, ensure reproducible builds via `uv.lock`, and optimize the Docker container by leveraging `uv`'s speed and efficiency.

## Goals
-   Replace `pyenv` and standard `venv` with `uv` for local development.
-   Integrate `uv` into the `Dockerfile` for dependency installation.
-   Utilize `uv.lock` for deterministic and reproducible builds.
-   Update project scripts and documentation to reflect the move to `uv`.

## Functional Requirements
-   **Local Development:**
    -   Developers should be able to set up their environment using `uv`.
    -   `uv run` should be used for executing commands and scripts.
    -   Dependency management should be handled through `uv sync` and `uv add`.
-   **Docker Integration:**
    -   The `Dockerfile` must install and use `uv` for environment setup.
    -   The final image should be optimized for size and performance.
-   **Lockfile Management:**
    -   A `uv.lock` file must be generated and committed to the repository.
-   **Task Automation:**
    -   The `Makefile` must be updated to use `uv` for all Python-related tasks.
-   **Documentation:**
    -   Update `README.md` and Conductor project documents to reflect the new workflow.

## Non-Functional Requirements
-   **Performance:** The build process (local and Docker) should be significantly faster with `uv`.
-   **Reproducibility:** All environments (local, CI, production) should use the same dependency versions.

## Acceptance Criteria
-   `uv` is successfully used to manage the Python 3.12 environment locally.
-   The `Dockerfile` builds successfully and runs the application using `uv`.
-   All `Makefile` commands (`lint`, `test`, `main`) function correctly with `uv`.
-   Legacy files (e.g., `requirements.txt`) are removed or integrated into `pyproject.toml`.
-   The project documentation accurately describes the new `uv`-based setup.

## Out of Scope
-   Migrating to a different Python version (staying with 3.12).
-   Changing the core application logic.
