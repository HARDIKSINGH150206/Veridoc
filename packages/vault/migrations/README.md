# Vault migrations (Alembic)

The vault database (SQLite, WAL mode) is created and changed only by Alembic migrations. Owner: Area 3 (Hardik). Other areas ask for schema changes in an issue and never add migrations ([ADR-021](../../../docs/DECISIONS.md), [DATA_MODEL](../../../docs/DATA_MODEL.md)).

Status: `0001` is an empty baseline. `0002` adds the two tables that do not depend on `packages/contracts`: `audit_event` and `leaf`, both insert-only with their triggers (issue #23, FR-VLT-004). The models are in `../models.py` and are `target_metadata` in `env.py`. The other tables (deal, messages, versions, recaps and the rest) wait for the agreed contracts (PR #40).

## Layout

| Path | Purpose |
|---|---|
| `../alembic.ini` | Alembic configuration. Holds no database URL |
| `env.py` | Reads the URL from `-x url=...` or from `packages.vault.migrate`; uses SQLite batch mode |
| `script.py.mako` | Template for new revision files |
| `versions/` | One file per revision, named `NNNN_short_name.py` |
| `../migrate.py` | `upgrade(url)` and `downgrade(url)` for code and tests; the caller supplies the URL |

## Run migrations

From the repository root:

```
uv run alembic -c packages/vault/alembic.ini -x url=sqlite:///<path-to-vault-database> upgrade head
uv run alembic -c packages/vault/alembic.ini -x url=sqlite:///<path-to-vault-database> current
```

From code (the API layer builds the URL from `settings.home`; nothing is hardcoded):

```python
from packages.vault.migrate import upgrade

upgrade(database_url)
```

## Add a migration

1. Branch from `dev`: `feat/vault-<name>`. Only Area 3 does this.
2. Create the revision: `uv run alembic -c packages/vault/alembic.ini revision -m "short name" --rev-id 0002` (use the next number). Rename the file to `0002_short_name.py` if needed.
3. Write `upgrade()` and `downgrade()` with `op.*` calls. The models must match the contracts.
4. **Insert-only tables** (audit events, messages, versions, receipts and the others in DATA_MODEL section 4): create the table and then its two triggers in the same migration as raw SQL with `op.execute`, so UPDATE and DELETE abort:
   ```python
   op.execute("""CREATE TRIGGER audit_event_no_update BEFORE UPDATE ON audit_event
                 BEGIN SELECT RAISE(ABORT, 'audit_event is insert-only'); END""")
   op.execute("""CREATE TRIGGER audit_event_no_delete BEFORE DELETE ON audit_event
                 BEGIN SELECT RAISE(ABORT, 'audit_event is insert-only'); END""")
   ```
   Add a test that an UPDATE and a DELETE on that table fail.
5. Add tests in `packages/vault/tests/`: upgrade to head, downgrade, and the table's rules.
6. Never edit a revision that is already on `dev`; add a new one.
7. Add a changelog fragment in `changes/` and open a pull request into `dev`.

## Rules

- One head only. `packages/vault/tests/test_migrations.py` fails if there are two.
- File names start with the 4-digit revision id; ids go up by one.
- No database URL, path or secret in any migration.
- SQLite changes that alter a table use batch mode (`op.batch_alter_table`).
- Encryption is handled by the vault layer, not by migrations.

## Fix "multiple heads"

Two migrations with the same parent give two heads and `upgrade head` fails.

1. `uv run alembic -c packages/vault/alembic.ini heads` lists them.
2. `uv run alembic -c packages/vault/alembic.ini merge -m "merge heads" <head1> <head2>` creates a merge revision.
3. Run the migration tests on a scratch database.
4. Commit the merge revision in its own pull request, reviewed by Area 3.
