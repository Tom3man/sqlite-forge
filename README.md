# SQLite Forge

## Overview

SQLite Forge is a Python library designed to simplify and streamline operations on SQLite databases. It provides a robust API for creating, updating, and managing SQLite databases. Built on top of the lightweight and fast SQLite engine, this library adds additional functionality for managing database schemas, performing CRUD operations, and integrating with data analysis tools like pandas.

## Features

- **Easy Database Management**: Automate the creation, update, and deletion of SQLite databases.
- **Data Ingestion**: Seamlessly import data from pandas DataFrames directly into your SQLite database.
- **Schema Validation**: Ensures that the data conforms to the predefined database schema.
- **Query Execution**: Execute SQL queries and retrieve results directly into pandas DataFrames for further analysis.
- **Table Existence Check**: Quickly verify the existence of tables before performing operations to ensure stability and reliability.

## Installation

SQLite Forge requires Python 3.12 or higher. Here are the steps to install and set up the library:

1. **Direct Installation** (Add to your project):
    - Add the following line to your `requirements.txt`:
      ```
      git+https://github.com/yourusername/sqlite-forge.git
      ```
    - Or, add it to your `pyproject.toml`:
      ```
      sqlite-forge = { git = "https://github.com/yourusername/sqlite-forge.git" }
      ```

2. **Local Development**:
    - Clone the repository:
      ```bash
      git clone https://github.com/yourusername/sqlite-forge.git
      cd sqlite-forge
      ```

    - Set up a virtual environment (optional but recommended):
      ```bash
      python -m venv venv
      source venv/bin/activate  # On Windows use `venv\Scripts\activate`
      ```

    - Install dependencies:
      ```bash
      pip install -r requirements.txt
      ```

## Building Table Classes

Create a new database by building a table class that inherits from `SqliteDatabase`. Here's an example:


```python
from sqlite_forge.database import SqliteDatabase


class ExampleDatabase(SqliteDatabase):

    DEFAULT_PATH = "DATABASE_NAME"
    PRIMARY_KEY = ["PRIMARY_KEY_1", "PRIMARY_KEY_2"]
    DEFAULT_SCHEMA = {
        "PRIMARY_KEY_1": "VARCHAR(4)",   
        "PRIMARY_KEY_2": "VARCHAR(4)",
        "COLUMN_X": "VARCHAR(50)",
        "COLUMN_Y": "INT",
        "COLUMN_Z": "DATE",
    }
```

## Interactions

Once a table class has been built, the database can be interacted with using several common interaction methods.

To start interacting with the database via the table class, an instantiation must be made with the path to your database folder:

```python
from my_table_classes import ExampleDatabase


# Initialize your database settings
db = ExampleDatabase(database_path="/path/to/your/database/directory")
```

All example below will now utilise this instantiation.

### Creating a New Database

To create a new database from the defined table class:

```python
db.create_table(cursor)
```

### Dropping a Table

To safely drop an existing table:

```python
# Safely drop the table
db.drop_table(cursor)
```

### Ingesting Data from DataFrame

To ingest data from a pandas DataFrame:

```python
import pandas as pd

data = pd.DataFrame({
    'column1': [1, 2, 3],
    'column2': ['A', 'B', 'C']
})

db.ingest_dataframe(cursor, data)
```

