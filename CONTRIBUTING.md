# Contributing to SQLite Forge

Thanks for your interest in improving SQLite Forge.

## Setup

```bash
poetry install --with dev --with docs
```

## Local Quality Checks

```bash
poetry run ruff check .
poetry run mypy
poetry run pytest
poetry run mkdocs build --strict
```

## Pull Request Checklist

- Add or update tests for behaviour changes.
- Update `README.md` and `docs/` for user-facing changes.
- Add a changelog entry in `CHANGELOG.md` for release-impacting work.
