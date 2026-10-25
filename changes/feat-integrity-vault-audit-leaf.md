type: Added
area: 3
requirements: FR-VLT-001, FR-VLT-002, FR-VLT-004
summary: Vault migration 0002 adds the audit_event and leaf tables (the two that do not depend on the shared contracts) with BEFORE UPDATE and BEFORE DELETE triggers that abort, SQLAlchemy 2.0 models as Alembic's target metadata, and tests for the triggers, constraints, upgrade, downgrade and the documented CLI. alembic.ini now puts the repository root on the import path so the CLI works.
