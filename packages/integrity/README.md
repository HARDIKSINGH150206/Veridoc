Integrity primitives: hashing, canonical JSON, salted Merkle tree, echo code, version chain. Owner: Area 3 (Hardik). The anchoring/ subfolder is owned by Area 4. Tests go in packages/integrity/tests/.

All functions are pure: bytes or JSON in, bytes or text out. No I/O, no clock, no randomness (salts are passed in), no dependency on the contract shapes. The rules are in [docs/INTEGRITY_SPEC.md](../../docs/INTEGRITY_SPEC.md); any change here must update the spec and the test vectors in the same change.

| Module | What it does |
|---|---|
| `hashing.py` | SHA-256, the domain-separation prefix table, `domain_hash`, export file digest, hex helpers |
| `canonical.py` | `canonicalize` (pure RFC 8785 via `rfc8785`), `normalize_text` and `normalize_strings`, `canonical_record` |
| `merkle.py` | salted leaves (`leaf_hash`, `record_leaf`, `file_leaf`), `merkle_root`, `inclusion_proof`, `verify_inclusion` |
| `echo.py` | `derive_echo_code`, `normalize_code` |
| `chain.py` | `terms_digest`, `chain_link`, `chain_links` |
| `records.py` | plain records: recap, receipt, import record |

Rules worth knowing:
- Hash operands are raw bytes. Hex is for storage and display only.
- `canonicalize` normalises nothing. Record builders call `normalize_strings` (NFC and LF line endings on every string value, never on keys) first; `canonical_record` does both.
- Integers outside the safe range (+-(2^53 - 1)), NaN and infinities are rejected.
- An empty Merkle tree is rejected; a one-leaf tree's root is the leaf and its proof is empty; an odd node is carried up, never duplicated.
- Only the prefixes in `SALTED_LEAF_PREFIXES` make leaves; only those in `PLAIN_RECORD_PREFIXES` make plain records.

Tests (`uv run pytest packages/integrity`): known SHA-256 vectors, the RFC 8785 examples (data files in `tests/data/`, because a formatter must not touch their escape sequences), explicit tree shapes, and hypothesis properties (any changed leaf or reordering changes the root, every proof verifies, tampered proofs fail).
