import logging
from pathlib import Path

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover - Python < 3.8 compatibility
    PackageNotFoundError = None  # type: ignore
    version = None  # type: ignore

MODULE_PATH = Path(__file__).resolve().parent
REPO_PATH = MODULE_PATH.parent
DATABASE_PATH = str(REPO_PATH)

log = logging.getLogger("sqlite_forge")
log.addHandler(logging.NullHandler())

if version and PackageNotFoundError:
    try:
        __version__ = version("sqlite-forge")
    except PackageNotFoundError:
        __version__ = "0.0.0"
else:
    __version__ = "0.0.0"

from .database import SqliteDatabase
from .forger import BuildDatabase, sqlite3_process

__all__ = [
    "BuildDatabase",
    "SqliteDatabase",
    "sqlite3_process",
    "log",
    "DATABASE_PATH",
    "__version__",
]
