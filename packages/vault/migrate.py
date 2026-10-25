"""Run vault migrations from code. The caller supplies the database URL.

No path or URL is hardcoded here. The API layer builds the URL from `settings.home`.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config

INI_FILE = Path(__file__).resolve().parent / "alembic.ini"


def alembic_config(database_url: str | None = None) -> Config:
    """Return the Alembic configuration, with the database URL set if one is given."""
    config = Config(str(INI_FILE))
    if database_url is not None:
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def upgrade(database_url: str, revision: str = "head") -> None:
    """Bring the database up to a revision (default: the latest)."""
    command.upgrade(alembic_config(database_url), revision)


def downgrade(database_url: str, revision: str = "base") -> None:
    """Take the database down to a revision (default: empty). For tests and development only."""
    command.downgrade(alembic_config(database_url), revision)
