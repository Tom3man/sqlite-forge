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

To install SQLite Forge, you need to have Python installed on your system. SQLite Forge works best with Python 3.6 or higher (preferably 3.12 and higher).
The repository can be added in a requirements.txt or a pyproject.toml file for a repository that will be using and imported as a package. Alternativly it can be cloned locally.

## Building Table Classes

Table classes offer a form of data encapsulation and a pythonic way of interacting with a sqlite database.
To create a new database, a table class will need to be built that will inherit the SqliteDatabase abstract class. An example is shown below:

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

