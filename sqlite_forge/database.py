import logging
import sqlite3
from abc import ABC
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from sqlite_forge.forger import BuildDatabase, sqlite3_process

log = logging.getLogger(__name__)


class SqliteDatabase(BuildDatabase, ABC):
    """
    Class for managing SQLite database operations.
    """

    # Table name for database
    DEFAULT_PATH: str = None

    # Schema dictionary for database
    DEFAULT_SCHEMA: Dict[str, str] = None

    # Optional primary key(s) for database
    PRIMARY_KEY: Optional[List[str]] = None

    def __init__(self, *args, **kwargs):
        """
        Initialize the SqliteDatabase class.
        """
        super().__init__(*args, **kwargs)

    @sqlite3_process
    def drop_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Drop the specified table from the database if it exists.
        """
        # Drop the table if it exists and overwrite is True
        drop_query = f"DROP TABLE IF EXISTS {self.db_name};"
        cursor.execute(drop_query)
        log.info(f"Dropped existing table {self.db_name}.")

    @sqlite3_process
    def create_table(self, cursor: sqlite3.Cursor, overwrite: Optional[bool] = False) -> None:
        """
        Create a table in the database with composite primary keys.
        """
        # Check if the table already exists
        if self.exists():
            if overwrite:
                # Drop table
                self.drop_table()
            else:
                # Log and return if the table exists and overwrite is False
                log.info(f"Table {self.db_name} already exists and will not be overwritten.")
                return

        # Define individual columns with their data types
        columns_definitions = [f'{column_name} {column_type}' for column_name, column_type in self.DEFAULT_SCHEMA.items()]

        # Include primary key in the column definitions if specified
        if hasattr(self, 'PRIMARY_KEY') and self.PRIMARY_KEY:
            primary_key_clause = f"PRIMARY KEY ({', '.join(self.PRIMARY_KEY)})"
            columns_definitions.append(primary_key_clause)

        columns_definitions_str = ', '.join(columns_definitions)

        # Create the table with "IF NOT EXISTS" for safety
        create_table_query = f'CREATE TABLE IF NOT EXISTS {self.db_name} ({columns_definitions_str})'

        cursor.execute(create_table_query)
        log.info(f"Table {self.db_name} created successfully with composite primary keys.")

    @sqlite3_process
    def get_columns(self, cursor: sqlite3.Cursor) -> List[str]:
        """
        Retrieve column names from the database.
        """
        cursor.execute(f"PRAGMA table_info({self.db_name})")
        columns_info = cursor.fetchall()
        return [column_info[1] for column_info in columns_info]

    @sqlite3_process
    def execute_query(
        self, cursor: sqlite3.Cursor, query: str
    ) -> pd.DataFrame:
        """
        Execute a query and return results as a DataFrame.
        """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return pd.DataFrame(data, columns=columns)

    @staticmethod
    def _validate_headers(headers: List[str], schema: Dict[str, str]) -> None:
        """
        Validate column headers against the schema.
        """
        mismatched_headers = [
            header for header in headers if header.lower() not in map(
                str.lower, schema.keys())]
        if mismatched_headers:
            mismatched = ', '.join(mismatched_headers)
            raise ValueError(
                f"Following column(s) in imported file do not match the DEFAULT_SCHEMA: {mismatched}")

    @sqlite3_process
    def ingest_dataframe(
        self, cursor, df: pd.DataFrame, load_date: Optional[bool] = False
    ) -> None:
        """
        Ingest a pandas dataframe into database.
        """

        if load_date:
            df['LOAD_DATE'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        headers = df.columns.tolist()
        self._validate_headers(headers, self.DEFAULT_SCHEMA)
        for index, row in df.iterrows():
            insert_query = f"""
                INSERT INTO {self.db_name} ({', '.join(headers)})
                VALUES ({', '.join(['?' for _ in range(len(headers))])})"""
            cursor.execute(insert_query, tuple(row))
