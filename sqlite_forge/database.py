import sqlite3
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Union

import pandas as pd

from sqlite_forge import log
from sqlite_forge.forger import BuildDatabase, sqlite3_process


class SqliteDatabase(BuildDatabase, ABC):
    """
    Class for managing SQLite database operations.
    """

    # Table name for database
    DEFAULT_PATH: Optional[str] = None

    # Schema dictionary for database
    DEFAULT_SCHEMA: Optional[Dict[str, str]] = None

    # Optional primary key(s) for database
    PRIMARY_KEY: Optional[Sequence[str]] = None

    def __init__(self, *args, **kwargs):
        """
        Initialise the SqliteDatabase class.
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
    def create_table(self, cursor: sqlite3.Cursor, overwrite: bool = False) -> None:
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

        if self.DEFAULT_SCHEMA is None:
            raise ValueError("DEFAULT_SCHEMA must be set before creating a table.")

        # Define individual columns with their data types
        columns_definitions = [
            f'{column_name} {column_type}' for column_name, column_type in self.DEFAULT_SCHEMA.items()
        ]

        # Include primary key in the column definitions if specified
        if self.PRIMARY_KEY:
            primary_key_clause = f"PRIMARY KEY ({', '.join(self.PRIMARY_KEY)})"
            columns_definitions.append(primary_key_clause)

        columns_definitions_str = ', '.join(columns_definitions)

        # Create the table with "IF NOT EXISTS" for safety
        create_table_query = f'CREATE TABLE IF NOT EXISTS {self.db_name} ({columns_definitions_str})'

        cursor.execute(create_table_query)
        if self.PRIMARY_KEY:
            log.info(
                "Table %s created successfully with primary key(s): %s.",
                self.db_name,
                ", ".join(self.PRIMARY_KEY),
            )
        else:
            log.info("Table %s created successfully.", self.db_name)

    @sqlite3_process
    def get_columns(self, cursor: sqlite3.Cursor) -> List[str]:
        """
        Retrieve column names from the database.
        """
        cursor.execute(f"PRAGMA table_info({self.db_name})")
        columns_info = cursor.fetchall()
        return [column_info[1] for column_info in columns_info]

    @sqlite3_process
    def execute_query(self, cursor: sqlite3.Cursor, query: str) -> pd.DataFrame:
        """
        Execute a query and return results as a DataFrame.
        """
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
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
        self,
        cursor: sqlite3.Cursor,
        df: pd.DataFrame,
        load_date: bool = False,
        overwrite: bool = False,
    ) -> None:
        """
        Ingest a pandas dataframe into the database.

        If load_date is True, adds a LOAD_DATE column with the current datetime.
        If overwrite is True, updates existing records based on PRIMARY_KEY.
        """

        if load_date:
            df = df.copy()
            df['LOAD_DATE'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.DEFAULT_SCHEMA is None:
            raise ValueError("DEFAULT_SCHEMA must be set before ingesting a dataframe.")

        headers = df.columns.tolist()
        self._validate_headers(headers, self.DEFAULT_SCHEMA)

        if self.PRIMARY_KEY:
            # Pre-build the WHERE clause for existence check and update
            where_clause = " AND ".join([f"{key} = ?" for key in self.PRIMARY_KEY])

        insert_count = 0
        for _, row in df.iterrows():

            if self.PRIMARY_KEY:
                where_values = tuple(row[key] for key in self.PRIMARY_KEY)

                # Check if the record already exists
                cursor.execute(f"SELECT COUNT(*) FROM {self.db_name} WHERE {where_clause}", where_values)
                exists = cursor.fetchone()[0]

                if exists and overwrite:
                    # Record exists, update it
                    update_clause = ", ".join([f"{header} = ?" for header in headers if header not in self.PRIMARY_KEY])
                    update_values = tuple(row[header] for header in headers if header not in self.PRIMARY_KEY)
                    update_query = f"""
                        UPDATE {self.db_name}
                        SET {update_clause}
                        WHERE {where_clause}"""
                    cursor.execute(update_query, update_values + where_values)
                    insert_count += 1
                elif not exists:
                    # Record does not exist, insert it
                    insert_query = f"""
                        INSERT INTO {self.db_name} ({', '.join(headers)})
                        VALUES ({', '.join(['?' for _ in range(len(headers))])})"""
                    cursor.execute(insert_query, tuple(row[header] for header in headers))
                    insert_count += 1
            else:
                # No primary key provided, insert directly
                insert_query = f"""
                    INSERT INTO {self.db_name} ({', '.join(headers)})
                    VALUES ({', '.join(['?' for _ in range(len(headers))])})"""
                cursor.execute(insert_query, tuple(row[header] for header in headers))
                insert_count += 1

        log.info("%s rows written to %s; table now has %s rows.", insert_count, self.db_name, self.table_length)

    @property
    @sqlite3_process
    def table_length(self, cursor: sqlite3.Cursor) -> int:
        """
        Return the number of rows in the table.
        """
        cursor.execute(f"SELECT COUNT(*) FROM {self.db_name}")
        length = cursor.fetchone()[0]
        return length

    def fetch_table(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Return rows from the managed table as a DataFrame.
        """
        query = f"SELECT * FROM {self.db_name}"
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        return self.execute_query(query)

    def export_table(
        self,
        output_path: Union[str, Path],
        format: Literal["csv", "json", "parquet"] = "csv",
        limit: Optional[int] = None,
    ) -> Path:
        """
        Export table rows to a file.

        Args:
            output_path: Destination file path.
            format: Export format ("csv", "json", or "parquet").
            limit: Optional row limit before exporting.
        """
        df = self.fetch_table(limit=limit)
        path = Path(output_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "csv":
            df.to_csv(path, index=False)
        elif format == "json":
            df.to_json(path, orient="records", indent=2)
        elif format == "parquet":
            try:
                df.to_parquet(path, index=False)
            except ImportError as exc:
                raise ImportError(
                    "Parquet export requires an engine such as 'pyarrow' or 'fastparquet'."
                ) from exc
        else:
            raise ValueError("format must be one of: csv, json, parquet")

        log.info("Exported %s rows from %s to %s", len(df), self.db_name, path)
        return path
