import logging
import os
import sqlite3
from abc import ABC
from typing import Callable, Dict, Optional

log = logging.getLogger(__name__)


def sqlite3_process(func: Callable) -> Callable:
    """
    Decorator to manage SQLite database connection.
    """
    def func_wrapper(self, *args, **kwargs):

        # Connect to the SQLite database
        conn = sqlite3.connect(f"{self.database_path}/{self.db_name}.db")
        cursor = conn.cursor()

        # Execute the wrapped function
        output = func(self, cursor, *args, **kwargs)

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        return output
    return func_wrapper


class BuildDatabase(ABC):
    """
    Abstract base class for building a SQLite database.
    """

    DEFAULT_PATH: str = None
    DEFAULT_SCHEMA: Dict[str, str] = None

    def __init__(self, database_path: str, database_name: Optional[str] = None):
        """
        Initialize the BuildDatabase class.
        """
        if not self.DEFAULT_PATH or not self.DEFAULT_SCHEMA:
            raise ValueError("Both DEFAULT_PATH and DEFAULT_SCHEMA must be implemented in the inheriting child class!")
        if database_name:
            self.db_name = database_name
        else:
            self.db_name = self.DEFAULT_PATH
        self.database_path = database_path

    @property
    def database(self) -> str:
        """
        Get the full path of the database file.
        """
        db_path = f"{self.database_path}/{self.db_name}.db"
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database file '{db_path}' does not exist, please create first!")
        return db_path

    @property
    def conn(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database.
        """
        return sqlite3.connect(self.database)

    @sqlite3_process
    def exists(self, cursor: sqlite3.Cursor) -> bool:
        """
        Check if a specified table exists in the database.
        """
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.db_name}';"
        cursor.execute(query)
        return cursor.fetchone() is not None
