# SQLite Forge

SQLite Forge is a lightweight toolkit that helps you declare and maintain SQLite tables from Python. Define your schema once, then manage tables, run queries, and ingest pandas `DataFrame` objects without repeating boilerplate code.

## Highlights
- Declarative table definitions with schemas and optional multi-column primary keys.
- Safe helpers to create or drop tables and to check existence.
- DataFrame ingestion with optional incremental overwrites.
- Convenience wrappers to execute SQL queries and receive pandas `DataFrame` results.
- Minimal footprint with no ORM overhead.

## Installation

SQLite Forge supports Python 3.10 and newer.

### Using `pip`

```bash
pip install git+https://github.com/Tom3man/sqlite-forge.git
```

### Using Poetry

```bash
poetry add git+https://github.com/Tom3man/sqlite-forge.git
```

For local development you can clone the repository instead:

```bash
git clone https://github.com/Tom3man/sqlite-forge.git
cd sqlite-forge
poetry install
```

## Quick Start

Create a table class by inheriting from `SqliteDatabase` and supplying a default name, schema, and optional primary key definition.

```python
from sqlite_forge import SqliteDatabase


class ExampleTable(SqliteDatabase):
    DEFAULT_PATH = "example_table"
    PRIMARY_KEY = ("id",)
    DEFAULT_SCHEMA = {
        "id": "INTEGER",
        "name": "TEXT",
        "score": "REAL",
    }
```

Instantiate the table with a directory to store database files. You can then create tables, ingest dataframes, and run ad-hoc queries:

```python
from pathlib import Path
import pandas as pd

db = ExampleTable(database_path=Path("./data"))
db.create_table(overwrite=False)

df = pd.DataFrame(
    [
        {"id": 1, "name": "Alice", "score": 9.2},
        {"id": 2, "name": "Bob", "score": 8.7},
    ]
)

db.ingest_dataframe(df, overwrite=True)
results = db.execute_query("SELECT name, score FROM example_table ORDER BY score DESC;")
print(results)
```

### Dropping a Table

```python
db.drop_table()
```

### Checking Table Length

```python
row_count = db.table_length
```

## Development

We use [Poetry](https://python-poetry.org/) for dependency management.

```bash
poetry install
poetry run pytest
```

Formatting is not enforced, but running tools such as `ruff`, `black`, or `isort` locally is encouraged. See `CONTRIBUTING.md` for more details.

## License

This project is released under the MIT License. See `LICENSE` for more information.
