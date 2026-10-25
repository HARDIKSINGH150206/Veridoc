type: Added
area: 3
requirements: FR-VLT-001, FR-VLT-002
summary: Demo-mode route GET /api/vault/deals/{deal_id}/receipt returns a clearly fake receipt for the walking skeleton (issue #21): fixed placeholder hashes, spec_version "demo-fake-not-verifiable", no vault reads or writes, no clock. Outside demo mode it answers 404; until contracts PR #40 is merged it answers 503 and the contract-dependent tests skip.
