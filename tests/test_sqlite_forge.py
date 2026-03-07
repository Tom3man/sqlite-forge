from pathlib import Path

import pandas as pd
import pytest

from sqlite_forge import SqliteDatabase


class SampleTable(SqliteDatabase):
    DEFAULT_PATH = "sample_table"
    PRIMARY_KEY = ("id",)
    DEFAULT_SCHEMA = {
        "id": "INTEGER",
        "name": "TEXT",
        "score": "REAL",
    }


def test_create_and_drop_table(tmp_path: Path) -> None:
    table = SampleTable(database_path=tmp_path)

    assert not table.exists()

    table.create_table(overwrite=True)
    assert table.exists()
    assert table.table_length == 0

    table.drop_table()
    assert not table.exists()


def test_ingest_dataframe_with_overwrite(tmp_path: Path) -> None:
    table = SampleTable(database_path=tmp_path)
    table.create_table(overwrite=True)

    initial = pd.DataFrame(
        [
            {"id": 1, "name": "Alice", "score": 9.2},
            {"id": 2, "name": "Bob", "score": 8.7},
        ]
    )
    table.ingest_dataframe(initial)
    assert table.table_length == 2

    updated = pd.DataFrame(
        [
            {"id": 2, "name": "Bob", "score": 9.8},
            {"id": 3, "name": "Cara", "score": 7.5},
        ]
    )
    table.ingest_dataframe(updated, overwrite=True)
    assert table.table_length == 3

    results = table.execute_query("SELECT id, score FROM sample_table ORDER BY id")
    assert results.loc[results["id"] == 2, "score"].iloc[0] == pytest.approx(9.8)
    assert set(results["id"]) == {1, 2, 3}


def test_ingest_dataframe_with_invalid_headers(tmp_path: Path) -> None:
    table = SampleTable(database_path=tmp_path)
    table.create_table(overwrite=True)

    bad_df = pd.DataFrame([{"unknown": 1}])

    with pytest.raises(ValueError):
        table.ingest_dataframe(bad_df)


def test_fetch_table_with_limit(tmp_path: Path) -> None:
    table = SampleTable(database_path=tmp_path)
    table.create_table(overwrite=True)

    df = pd.DataFrame(
        [
            {"id": 1, "name": "Alice", "score": 9.2},
            {"id": 2, "name": "Bob", "score": 8.7},
            {"id": 3, "name": "Cara", "score": 7.9},
        ]
    )
    table.ingest_dataframe(df)

    limited = table.fetch_table(limit=2)
    assert len(limited) == 2


def test_export_table_csv_and_json(tmp_path: Path) -> None:
    table = SampleTable(database_path=tmp_path)
    table.create_table(overwrite=True)
    table.ingest_dataframe(pd.DataFrame([{"id": 1, "name": "Alice", "score": 9.2}]))

    csv_path = table.export_table(tmp_path / "out" / "table.csv", format="csv")
    json_path = table.export_table(tmp_path / "out" / "table.json", format="json")

    assert csv_path.exists()
    assert json_path.exists()
    assert csv_path.read_text(encoding="utf-8").startswith("id,name,score")
