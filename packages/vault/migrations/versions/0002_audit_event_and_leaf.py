"""audit_event and leaf tables, insert-only

The two vault tables that do not depend on the shared contracts (issue #23, FR-VLT-004). Both are
insert-only: BEFORE UPDATE and BEFORE DELETE triggers abort (DATA_MODEL section 4). Values are a
snapshot written out here, not imported, so this revision never changes when code changes.

Revision ID: 0002
Revises: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INSERT_ONLY = ("audit_event", "leaf")
ACTIONS = (
    "'import', 'confirm_term', 'correct_term', 'reject_term', 'seal', 'reveal', "
    "'create_version', 'send_recap', 'check_reply', 'export', 'setting_change', "
    "'safe_mode_change', 'delete_deal'"
)
SALTED_TYPES = "16, 17, 18, 19, 20, 21, 34"  # 0x10 to 0x15 and 0x22 (INTEGRITY_SPEC section 3)


def lower_hex(column: str, length: int) -> str:
    return f"length({column}) = {length} AND {column} NOT GLOB '*[^0-9a-f]*'"


def upgrade() -> None:
    op.create_table(
        "audit_event",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("deal_id", sa.String(), nullable=True),
        sa.Column("ts", sa.Text(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("detail", sa.LargeBinary(), nullable=False),
        sa.CheckConstraint("actor IN ('me', 'system')", name="ck_audit_event_actor"),
        sa.CheckConstraint(f"action IN ({ACTIONS})", name="ck_audit_event_action"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_event"),
    )
    op.create_index("ix_audit_event_deal_id", "audit_event", ["deal_id"])

    op.create_table(
        "leaf",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("deal_id", sa.String(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("type_byte", sa.Integer(), nullable=False),
        sa.Column("salt", sa.String(), nullable=False),
        sa.Column("payload_digest", sa.String(), nullable=False),
        sa.Column("leaf_hash", sa.String(), nullable=False),
        sa.Column("ref_table", sa.String(), nullable=False),
        sa.Column("ref_id", sa.String(), nullable=False),
        sa.CheckConstraint("seq >= 1", name="ck_leaf_seq"),
        sa.CheckConstraint(f"type_byte IN ({SALTED_TYPES})", name="ck_leaf_type_byte"),
        sa.CheckConstraint(lower_hex("salt", 32), name="ck_leaf_salt"),
        sa.CheckConstraint(lower_hex("payload_digest", 64), name="ck_leaf_payload_digest"),
        sa.CheckConstraint(lower_hex("leaf_hash", 64), name="ck_leaf_leaf_hash"),
        sa.PrimaryKeyConstraint("id", name="pk_leaf"),
        sa.UniqueConstraint("deal_id", "seq", name="uq_leaf_deal_id"),
    )

    for table in INSERT_ONLY:
        op.execute(
            f"CREATE TRIGGER {table}_no_update BEFORE UPDATE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} is insert-only'); END"
        )
        op.execute(
            f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} is insert-only'); END"
        )


def downgrade() -> None:
    for table in INSERT_ONLY:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_delete")
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_update")
    op.drop_table("leaf")
    op.drop_index("ix_audit_event_deal_id", table_name="audit_event")
    op.drop_table("audit_event")
