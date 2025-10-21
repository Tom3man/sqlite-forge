import logging
import sqlite3
from abc import ABC
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, Optional, TypeVar, Union

log = logging.getLogger(__name__)

T = TypeVar("T")
DatabasePath = Union[str, Path]


def sqlite3_process(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to manage SQLite database connection.
    """
    @wraps(func)
    def func_wrapper(self, *args, **kwargs) -> T:
        database_dir = Path(self.database_path)
        database_dir.mkdir(parents=True, exist_ok=True)
        db_file = database_dir / f"{self.db_name}.db"

        conn = sqlite3.connect(str(db_file))
        try:
            cursor = conn.cursor()
            result = func(self, cursor, *args, **kwargs)
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        else:
            conn.commit()
            return result
        finally:
            conn.close()

    return func_wrapper


class BuildDatabase(ABC):
    """
    Abstract base class for building a SQLite database.
    """

    DEFAULT_PATH: Optional[str] = None
    DEFAULT_SCHEMA: Optional[Dict[str, str]] = None

    def __init__(self, database_path: DatabasePath, database_name: Optional[str] = None) -> None:
        """
        Initialize the BuildDatabase class.
        """
        if not self.DEFAULT_PATH or not self.DEFAULT_SCHEMA:
            raise ValueError("Both DEFAULT_PATH and DEFAULT_SCHEMA must be implemented in the inheriting child class!")
        self.db_name = database_name or self.DEFAULT_PATH
        self.database_path = Path(database_path).expanduser()

    @property
    def database(self) -> str:
        """
        Get the full path of the database file.
        """
        db_path = self.database_path / f"{self.db_name}.db"
        if not db_path.exists():
            raise FileNotFoundError(
                f"Database file '{db_path}' does not exist, please create first!")
        return str(db_path)

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
