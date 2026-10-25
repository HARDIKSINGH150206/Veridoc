SQLite storage, encryption, audit table, dispute pack. Owner: Area 3. Tests go in packages/vault/tests/.

Status: the Alembic scaffolding exists (migrations/README.md); the contract-dependent tables are issue #57. `fake_receipt.py` is a demo-only stub for the walking skeleton (issue #21): its hashes are fixed placeholders and it can never verify.

## Demo record (#31)

`demo_record.record_demo` is a pure builder for the walking skeleton: salted message leaves (`0x10`), the Merkle root, one agreement version (terms sorted by key, `terms_digest`, chain link) and the receipt envelope, all with the real functions from `packages/integrity`. The receipt verifies by the steps of INTEGRITY_SPEC section 10, but its `spec_version` is `demo-skeleton-not-for-evidence`, which no verifier supports, so it cannot be mistaken for evidence. Only message leaves are recorded (term and confirmation leaves come with the real vault, #57). `POST /api/vault/samples/{sample_id}/record` (demo mode only) accepts only terms confirmed by the primary user, draws fresh salts per call and writes nothing. The separate fake receipt route (`GET /api/vault/deals/{deal_id}/receipt`) is unchanged.
