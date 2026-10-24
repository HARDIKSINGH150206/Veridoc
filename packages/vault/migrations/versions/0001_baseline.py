"""baseline: empty, no tables yet

The tables wait for the agreed data shapes (packages/contracts, PR #40). This revision only
gives Alembic a starting point so later migrations have a parent.

Revision ID: 0001
Revises: none
"""

from collections.abc import Sequence

revision = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
