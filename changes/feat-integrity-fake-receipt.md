type: Added
area: 3
requirements: FR-VLT-001, FR-VLT-002
summary: Demo-mode route GET /api/vault/deals/{deal_id}/receipt returns a clearly fake receipt envelope (contracts v0.2.0) for the walking skeleton (issue #21): fixed placeholder hashes, spec_version "demo-fake-not-verifiable", no vault reads or writes, no clock, and a receipt_hash that never verifies. Outside demo mode it answers 404; deal ids must be lowercase UUIDs.
