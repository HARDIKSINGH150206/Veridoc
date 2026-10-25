"""Tests for the audit_event and leaf tables and their insert-only triggers (issue #23, FR-VLT-004).

Written before the migration. Every test runs `upgrade head` on a fresh scratch vault.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import DBAPIError

from packages.integrity.hashing import PREFIXES, SALTED_LEAF_PREFIXES
from packages.vault.migrate import downgrade, upgrade
from packages.vault.models import AUDIT_ACTIONS, INSERT_ONLY_TABLES, Base

HEX64 = "ab" * 32
SALT = "cd" * 16


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    database_url = f"sqlite:///{tmp_path / 'vault.sqlite'}"
    upgrade(database_url)
    made = create_engine(database_url)
    yield made
    made.dispose()


def audit_row(**changes: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "a1",
        "deal_id": "d1",
        "ts": "2026-10-12T10:02:00+05:30",
        "actor": "me",
        "action": "import",
        "detail": b"\x00ciphertext",
    }
    row.update(changes)
    return row


def leaf_row(**changes: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "l1",
        "deal_id": "d1",
        "seq": 1,
        "type_byte": PREFIXES["MESSAGE"],
        "salt": SALT,
        "payload_digest": HEX64,
        "leaf_hash": HEX64,
        "ref_table": "message",
        "ref_id": "m1",
    }
    row.update(changes)
    return row


def insert(engine: Engine, table: str, row: dict[str, Any]) -> None:
    columns = ", ".join(row)
    values = ", ".join(f":{name}" for name in row)
    with engine.begin() as connection:
        connection.execute(text(f"INSERT INTO {table} ({columns}) VALUES ({values})"), row)


def run(engine: Engine, statement: str) -> None:
    with engine.begin() as connection:
        connection.execute(text(statement))


def test_insert_only_tables_are_the_audit_and_leaf_tables() -> None:
    assert set(INSERT_ONLY_TABLES) == {"audit_event", "leaf"}


@pytest.mark.parametrize("table", INSERT_ONLY_TABLES)
def test_both_triggers_exist_after_upgrade_head(engine: Engine, table: str) -> None:
    """Guards against a later batch migration rebuilding a table and silently dropping them."""
    with engine.connect() as connection:
        names = set(
            connection.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = :t"),
                {"t": table},
            ).scalars()
        )
    assert names == {f"{table}_no_update", f"{table}_no_delete"}


@pytest.mark.parametrize(
    ("table", "row", "column"),
    [("audit_event", audit_row(), "actor"), ("leaf", leaf_row(), "ref_id")],
)
def test_update_and_delete_are_rejected(
    engine: Engine, table: str, row: dict[str, Any], column: str
) -> None:
    insert(engine, table, row)
    with pytest.raises(DBAPIError, match=f"{table} is insert-only"):
        run(engine, f"UPDATE {table} SET {column} = 'system'")
    with pytest.raises(DBAPIError, match=f"{table} is insert-only"):
        run(engine, f"DELETE FROM {table}")
    with engine.connect() as connection:
        assert connection.execute(text(f"SELECT count(*) FROM {table}")).scalar() == 1


def test_audit_event_accepts_every_documented_action(engine: Engine) -> None:
    for number, action in enumerate(AUDIT_ACTIONS):
        insert(engine, "audit_event", audit_row(id=f"a{number}", action=action, deal_id=None))
    assert len(AUDIT_ACTIONS) == 13


@pytest.mark.parametrize(
    "changes",
    [{"actor": "ai"}, {"action": "edit_message"}, {"ts": None}, {"detail": None}],
    ids=["actor", "action", "ts-null", "detail-null"],
)
def test_audit_event_rejects_invalid_rows(engine: Engine, changes: dict[str, Any]) -> None:
    with pytest.raises(DBAPIError):
        insert(engine, "audit_event", audit_row(**changes))


def test_leaf_accepts_every_salted_type_and_no_other(engine: Engine) -> None:
    for number, prefix in enumerate(sorted(SALTED_LEAF_PREFIXES), start=1):
        insert(engine, "leaf", leaf_row(id=f"l{number}", seq=number, type_byte=prefix))
    plain = set(PREFIXES.values()) - SALTED_LEAF_PREFIXES
    for number, prefix in enumerate(sorted(plain), start=100):
        with pytest.raises(DBAPIError):
            insert(engine, "leaf", leaf_row(id=f"x{number}", seq=number, type_byte=prefix))


@pytest.mark.parametrize(
    "changes",
    [
        {"seq": 0},
        {"salt": "cd" * 15},
        {"salt": "CD" * 16},
        {"payload_digest": "ab" * 31},
        {"leaf_hash": "AB" * 32},
        {"leaf_hash": "zz" * 32},
        {"ref_table": None},
        {"deal_id": None},
    ],
    ids=[
        "seq-zero",
        "salt-short",
        "salt-upper",
        "digest-short",
        "hash-upper",
        "hash-not-hex",
        "ref-null",
        "deal-null",
    ],
)
def test_leaf_rejects_invalid_rows(engine: Engine, changes: dict[str, Any]) -> None:
    with pytest.raises(DBAPIError):
        insert(engine, "leaf", leaf_row(**changes))


def test_leaf_sequence_is_unique_per_deal(engine: Engine) -> None:
    insert(engine, "leaf", leaf_row())
    insert(engine, "leaf", leaf_row(id="l2", deal_id="d2"))
    with pytest.raises(DBAPIError):
        insert(engine, "leaf", leaf_row(id="l3"))


def test_models_match_the_migrated_schema(engine: Engine) -> None:
    with engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert differences == []


def test_deal_id_is_indexed_on_both_tables(engine: Engine) -> None:
    inspector = inspect(engine)
    for table in INSERT_ONLY_TABLES:
        indexed = {col for ix in inspector.get_indexes(table) for col in ix["column_names"]}
        unique = {
            col for uq in inspector.get_unique_constraints(table) for col in uq["column_names"]
        }
        assert "deal_id" in indexed | unique, table


def test_downgrade_to_the_baseline_removes_tables_and_triggers(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'vault.sqlite'}"
    upgrade(database_url)
    downgrade(database_url, "0001")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        left = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type IN ('table', 'trigger')")
        ).scalars()
        assert set(left) == {"alembic_version"}
    engine.dispose()
