# Python Style Guide for Gemini Reviews

This document outlines the coding style guidelines for this Python project. It serves as a reference for developers and as a basis for code reviews conducted by humans or AI assistants like Gemini. The primary goal is to maintain a consistent, readable, and high-quality codebase.

## Core Principle: PEP 8

The foundational style guide for this project is [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

All Python code should adhere to the conventions described in PEP 8, with the key exception noted below. Consistency is paramount, as it improves readability, reduces cognitive load, and makes the code easier to maintain.

## Exceptions to PEP 8

While we adhere to PEP 8, we make the following exception to better suit our development workflow.

### Line Length (PEP 8 rule E501)

PEP 8 suggests a line limit of 79 characters for code. **This project does not enforce a strict line length limit.**

**Rationale:**
*   **Modern Displays:** Most modern development environments and displays can comfortably accommodate lines longer than 79 characters.
*   **Improved Readability:** Forcing line breaks can sometimes harm readability, especially for complex logical conditions, function signatures with many arguments, or long string literals. We prioritize logical structure over arbitrary line length limits.
*   **Reduced Code Churn:** It avoids unnecessary commits that only reformat lines for being slightly over the limit.

**Guideline for Reviews:**
While there is no hard limit, reviewers (human or AI) should still use their judgment. If a line is excessively long and difficult to read, it should be flagged. The focus should be on whether the code is clear and understandable, not on its character count.

## Tooling Configuration

To enforce our style guide automatically, you can configure your linter to ignore line length warnings.

### Flake8

If you are using `flake8`, you can ignore the `E501` (line too long) error by adding it to the `ignore` list in your configuration file (e.g., `.flake8`, `setup.cfg`, or `pyproject.toml`).

**Example for `.flake8`:**
```ini
[flake8]
ignore =
    # We don't enforce line length
    E501
```
