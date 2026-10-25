"""Alembic environment for the vault database.

The URL comes from `-x url=...` or from the `sqlalchemy.url` option set by
packages.vault.migrate. It is never read from a file or hardcoded.
"""

from alembic import context
from sqlalchemy import create_engine, pool

from packages.vault.models import Base

config = context.config

target_metadata = Base.metadata


def database_url() -> str:
    url = context.get_x_argument(as_dictionary=True).get("url") or config.get_main_option(
        "sqlalchemy.url"
    )
    if not url:
        raise RuntimeError(
            "No database URL. Pass -x url=sqlite:///<path> or use packages.vault.migrate."
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
