"""Tests for the Alembic scaffolding (written before it). No tables exist yet."""

import re
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from packages.vault.migrate import alembic_config, downgrade, upgrade

VAULT = Path(__file__).resolve().parent.parent
VERSIONS = VAULT / "migrations" / "versions"


def url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'vault.sqlite'}"


def user_tables(database_url: str) -> set[str]:
    return set(inspect(create_engine(database_url)).get_table_names()) - {"alembic_version"}


def test_upgrade_head_creates_only_the_version_table(tmp_path: Path) -> None:
    database_url = url(tmp_path)
    upgrade(database_url)
    tables = set(inspect(create_engine(database_url)).get_table_names())
    assert tables == {"alembic_version"}


def test_baseline_is_empty_no_tables_yet(tmp_path: Path) -> None:
    database_url = url(tmp_path)
    upgrade(database_url)
    assert user_tables(database_url) == set()


def test_downgrade_to_base_works(tmp_path: Path) -> None:
    database_url = url(tmp_path)
    upgrade(database_url)
    downgrade(database_url)
    assert user_tables(database_url) == set()


def test_upgrade_twice_is_harmless(tmp_path: Path) -> None:
    database_url = url(tmp_path)
    upgrade(database_url)
    upgrade(database_url)


def test_there_is_exactly_one_head() -> None:
    """Two heads break `alembic upgrade head`. See migrations/README.md to fix."""
    script = ScriptDirectory.from_config(alembic_config())
    assert len(script.get_heads()) == 1


def test_the_baseline_revision_exists_and_is_first() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    base = script.get_revision("0001")
    assert base is not None and base.down_revision is None


def test_revision_files_are_named_after_their_revision() -> None:
    files = [p for p in VERSIONS.glob("*.py") if p.name != "__init__.py"]
    assert files
    for path in files:
        match = re.match(r"^(\d{4})_[a-z0-9_]+\.py$", path.name)
        assert match, f"{path.name} must look like 0002_short_name.py"
        text = path.read_text(encoding="utf-8")
        assert f'revision = "{match.group(1)}"' in text


def test_the_ini_file_holds_no_database_url() -> None:
    ini = (VAULT / "alembic.ini").read_text(encoding="utf-8")
    assert not re.search(r"^sqlalchemy\.url\s*=\s*\S", ini, re.M)


def test_missing_url_gives_a_clear_error() -> None:
    from alembic import command

    with pytest.raises(RuntimeError, match="database URL"):
        command.upgrade(Config(str(VAULT / "alembic.ini")), "head")
