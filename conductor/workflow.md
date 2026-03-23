# Project Workflow: Conductor Methodology

## Core Principles
- **Test-Driven Development (TDD):** Write tests before implementing features.
- **Incremental Progress:** Break down tracks into small, manageable phases and tasks.
- **Continuous Documentation:** Keep specs and plans updated as the project evolves.

## Phase and Task Structure
1.  **Phase 1: Research and Specification:** Understand requirements and define the technical approach.
2.  **Phase 2: Test Infrastructure:** Set up necessary testing environments and utilities.
3.  **Phase 3: Implementation:** Develop the features using TDD.
4.  **Phase 4: Verification and Finalization:** Ensure all tests pass and requirements are met.

## Commit and Summary Strategy
- **Commit Frequency:** Commits will be performed after each **Phase** is complete.
- **Task Summaries:** Detailed summaries of the work performed will be included in the **Commit Message Body**.

## Quality Standards
- **Test Coverage:** All new code must maintain a minimum of **80%** test coverage.
- **Linting:** All code must pass `flake8` and `mypy` checks.
- **Documentation:** Every track must have a corresponding `spec.md` and `plan.md`.

## Phase Completion Verification and Checkpointing Protocol
At the end of each phase, a mandatory verification task must be completed:
`- [ ] Task: Conductor - User Manual Verification '<Phase Name>' (Protocol in workflow.md)`

The verification involves:
1.  Running the full test suite and ensuring all tests pass.
2.  Verifying the required test coverage percentage is met.
3.  Reviewing the implemented code against the `spec.md`.
4.  Updating the `plan.md` to reflect the current state.
