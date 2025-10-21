# Contributing to SQLite Forge

Thanks for your interest in improving SQLite Forge! This document outlines a short checklist to help you get started quickly.

## Getting Started

- Fork the repository and create a feature branch from `main`.
- Install dependencies with [Poetry](https://python-poetry.org/):
  ```bash
  poetry install
  ```
- Activate the virtual environment when developing locally:
  ```bash
  poetry shell
  ```

## Development Workflow

- Add tests for any new behaviour or bug fix. Place unit tests under `tests/`.
- Keep code style consistent. We recommend running `ruff` or `black`/`isort` if you have them installed locally, although the project does not currently enforce a specific formatter.
- Run the test suite before opening a pull request:
  ```bash
  poetry run pytest
  ```

## Pull Request Checklist

- Describe the change clearly and link to any relevant issues.
- Ensure CI checks pass (linting, tests, and packaging checks when available).
- Update documentation (including the README) when you add or modify behaviour.

By following these guidelines we can keep SQLite Forge stable and welcoming for contributors. Thanks again for helping out!
