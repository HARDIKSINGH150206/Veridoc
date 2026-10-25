"""SQLAlchemy 2.0 models of the vault tables (docs/DATA_MODEL.md section 3).

Only the tables that do not depend on the shared contracts exist so far: the audit table and the
evidence leaves. Both are insert-only. The UPDATE and DELETE triggers live in the Alembic
migration as raw SQL (ADR-021), never here, so a model change cannot drop them.
"""

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from packages.integrity.hashing import SALTED_LEAF_PREFIXES

AUDIT_ACTORS: tuple[str, ...] = ("me", "system")
AUDIT_ACTIONS: tuple[str, ...] = (
    "import",
    "confirm_term",
    "correct_term",
    "reject_term",
    "seal",
    "reveal",
    "create_version",
    "send_recap",
    "check_reply",
    "export",
    "setting_change",
    "safe_mode_change",
    "delete_deal",
)

INSERT_ONLY_TABLES: tuple[str, ...] = ("audit_event", "leaf")
"""Tables whose rows may never be updated or deleted (DATA_MODEL section 4)."""


def _quoted(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def _lower_hex(column: str, length: int) -> str:
    return f"length({column}) = {length} AND {column} NOT GLOB '*[^0-9a-f]*'"


class Base(DeclarativeBase):
    """Declarative base. Constraint names are fixed so migrations can refer to them."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class AuditEvent(Base):
    """One audit entry: imports, confirmations, corrections, seals, exports, settings.

    `detail` holds AES-GCM ciphertext of the JSON detail (DATA_MODEL section 5), never plain text.
    Requirements: FR-VLT-004.
    """

    __tablename__ = "audit_event"
    __table_args__ = (
        CheckConstraint(f"actor IN ({_quoted(AUDIT_ACTORS)})", name="actor"),
        CheckConstraint(f"action IN ({_quoted(AUDIT_ACTIONS)})", name="action"),
        Index("ix_audit_event_deal_id", "deal_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    deal_id: Mapped[str | None] = mapped_column(String)
    ts: Mapped[str] = mapped_column(Text)
    actor: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    detail: Mapped[bytes] = mapped_column(LargeBinary)


class Leaf(Base):
    """One salted Merkle leaf of a deal (INTEGRITY_SPEC section 5), pointing at its record.

    Hashes and salts are lowercase hex (INTEGRITY_SPEC section 2: hex for storage).
    Requirements: FR-VLT-001, FR-VLT-002, FR-VLT-004.
    """

    __tablename__ = "leaf"
    __table_args__ = (
        UniqueConstraint("deal_id", "seq", name="uq_leaf_deal_id"),
        CheckConstraint("seq >= 1", name="seq"),
        CheckConstraint(
            f"type_byte IN ({', '.join(str(p) for p in sorted(SALTED_LEAF_PREFIXES))})",
            name="type_byte",
        ),
        CheckConstraint(_lower_hex("salt", 32), name="salt"),
        CheckConstraint(_lower_hex("payload_digest", 64), name="payload_digest"),
        CheckConstraint(_lower_hex("leaf_hash", 64), name="leaf_hash"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    deal_id: Mapped[str] = mapped_column(String)
    seq: Mapped[int] = mapped_column(Integer)
    type_byte: Mapped[int] = mapped_column(Integer)
    salt: Mapped[str] = mapped_column(String)
    payload_digest: Mapped[str] = mapped_column(String)
    leaf_hash: Mapped[str] = mapped_column(String)
    ref_table: Mapped[str] = mapped_column(String)
    ref_id: Mapped[str] = mapped_column(String)
