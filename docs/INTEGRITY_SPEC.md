# Integrity Specification

This document defines exactly how VeriDoc hashes records, builds the Merkle tree and version chain, derives the echo code, and verifies a receipt. Python (`packages/integrity`) and JavaScript (`apps/verify`) must follow it byte for byte. Background on where the design ideas come from is in [PRIOR_WORK](PRIOR_WORK.md).

Last updated: 2026-10-25
Status: Draft v1

All byte values, field lists and the spec version below are **proposed** and become final only when the cross-language test vectors in `test-vectors/integrity/` pass in both languages. Any change to this file must update the vectors in the same change.

## 1. Scope and claims

| VeriDoc can show | VeriDoc cannot show |
|---|---|
| A record is unchanged since it was saved (tamper-evident). | That the original WhatsApp export was genuine. |
| The order and linkage of agreement versions. | That the device clock was correct (unless the root is anchored). |
| That a recap's echo code matches that exact recap text. | Who physically typed a reply. |

The AI layer never writes to anything in this document. Only the integrity engine computes hashes, and it takes only human-confirmed data.

## 2. Primitives

| Item | Definition |
|---|---|
| Hash function | SHA-256. Output is 32 bytes. |
| `H(x)` | SHA-256 of the byte string `x`. |
| `||` | Byte concatenation. Every hash operand (`salt`, `payload_digest`, `recap_hash`, `root`, `link`, node hashes) is a raw 32-byte (salt: 16-byte) value, never hex text. |
| Text encoding | UTF-8, no BOM. |
| Text normalisation | `normalize_text(s)`: Unicode NFC, then every `\r\n` and lone `\r` becomes `\n`. The record builders apply it to **every string value** of a record before canonicalisation. **Keys are never normalised.** `canonicalize` itself is pure RFC 8785 and normalises nothing. The raw imported export file is the exception: it is hashed as raw bytes with no normalisation (section 4.1). |
| Hex encoding | Lowercase hexadecimal, 64 characters per hash, **for storage and display only**. Hashing always works on raw bytes. |
| Salt | 16 random bytes from the operating system's secure random source, one per leaf, stored in the vault. |
| Timestamps | ISO 8601 with offset, for example `2026-10-12T10:02:00+05:30`. Taken from the device clock unless anchored. |

## 3. Domain separation

Every hash input starts with one prefix byte that names the record type. A hash made for one type can never be valid for another.

**Rule.** Every record that selective disclosure could hide is a **salted leaf** (section 5). Structural records (chain links, roots, receipts, versions, recaps, the import record) are **plain**: `H(prefix || JCS(object))`, without salt.

| Byte | Record type | Form |
|---|---|---|
| `0x01` | Merkle inner node | structural |
| `0x10` | Message | salted leaf |
| `0x11` | Voice-note audio (raw file bytes) | salted leaf |
| `0x12` | Transcript span (one leaf per span) | salted leaf |
| `0x13` | Handshake answer-set seal | salted leaf |
| `0x14` | Attachment (non-audio media, raw file bytes) | salted leaf |
| `0x15` | Term (one confirmed term) | salted leaf |
| `0x16` | Import record (includes the export digest) | plain |
| `0x20` | Agreed-terms set of a version | plain |
| `0x21` | Recap | plain |
| `0x22` | Confirmation (verified reply) | salted leaf |
| `0x30` | Version-chain link | plain |
| `0x40` | Receipt | plain |
| `0x50` | Echo-code derivation | plain |

A recap is plain because the echo code is derived from its hash, which anyone holding the recap text must be able to recompute. `0x15` and `0x16` are new in this version. `0x12` is one leaf per transcript span, so a single span can be disclosed.

Byte `0x00` is reserved and must never be used as a prefix.

## 4. Canonical serialisation

Structured records are serialised with RFC 8785 JSON Canonicalization Scheme (JCS) before hashing: sorted keys, no insignificant whitespace, UTF-8, ECMAScript number formatting. Implementations: Python `rfc8785` and npm `canonicalize`, both pinned.

Building a record's canonical bytes is always: `normalize_text` on every string value (keys untouched), then JCS.

Numbers:
- Large or exact values are **strings**: money (integer paise, for example `"4800000"`), quantities and identifiers.
- Integers must lie in the safe range -(2^53 - 1) to 2^53 - 1. An integer outside it is **rejected** with an error; it is never rounded.
- Floats are allowed only where a contract needs them (durations, confidence). NaN and infinities are rejected.
- Dates inside records are ISO 8601 strings.

### 4.1 The imported export file

The original imported export file (the `.txt` or `.zip` as the user gave it) is hashed as **raw bytes with no normalisation and no prefix**: `export_digest = H(raw file bytes)`, so anyone can check it with a standard `sha256sum`. The digest is stored in the import record (`0x16`), which is a plain record: `H(0x16 || JCS(import_record))`.

Required fields by record type (field names are final once the contracts package is agreed):

| Type | Fields in the canonical object |
|---|---|
| Message | `id`, `sender`, `ts`, `text`, `attachment` (file name or null), `source` (`export`, `paste` or `simulator`) |
| Transcript span | `transcript_id`, `voice_note_id`, `model`, `model_version`, `language`, `index`, `start_ms`, `end_ms`, `text` (each span repeats the header so it can be disclosed alone) |
| Term | `deal_id`, `key`, `value`, `unit`, `sources`, `confirmed_by` |
| Import record | `deal_id`, `export_digest` (hex), `file_name`, `message_count`, `imported_at` |
| Handshake answer set | `deal_id`, `party`, `order` (1 or 2), `mode` (`reply` or `handover`), `answers` (key to value), `sealed_at` |
| Agreed-terms set | `deal_id`, `version`, `playbook`, `playbook_version`, `terms` (sorted by key; each with `key`, `value`, `unit`, `sources`, `confirmed_by`) |

The field names above are indicative. The primitives and their test vectors accept any JSON; the exact record shapes are fixed with the contracts (PR #40). The draft contracts use seconds as floats for transcript times where this table uses integer milliseconds; they are aligned when the contracts are agreed (OPEN_QUESTIONS Q-61).
| Recap | `deal_id`, `version`, `language`, `lines` (each with `term_key`, `text`, `sources`), `text` |
| Confirmation | `deal_id`, `version`, `party`, `reply_text`, `reply_ts`, `code`, `sender_entered_by_user` (boolean) |

## 5. Leaves

```
payload_digest = H(payload)                    # payload = JCS bytes, or raw file bytes for audio and attachments
leaf           = H(type_byte || salt || payload_digest)
```

Hashing the payload first lets large audio files stream through the hash without being held in memory. The `salt` is stored with the leaf in the vault. A bundle includes the salt for every disclosed leaf and only the leaf hash for others, so an undisclosed leaf cannot be guessed from its likely content.

Audio and its transcript spans are separate leaves (`0x11`, `0x12`). The leaf form above applies to `0x10` to `0x15` and `0x22`; the payload of `0x11` and `0x14` is the raw file bytes and the payload of the others is the canonical JSON (after `normalize_text`).

## 6. Merkle tree

- Leaves are ordered by their sequence number in the deal (the order in which they were added to the vault).
- Inner node: `node = H(0x01 || left || right)`.
- If a level has an odd number of nodes, the last node is carried up to the next level unchanged. It is never duplicated.
- **An empty tree is rejected with an error**; a receipt requires at least one leaf.
- A tree of one leaf has that leaf hash as its root, and its inclusion proof is empty.
- An inclusion proof lists, from the bottom up, each sibling hash with the side it is on (`left` or `right`). A level on which the node was carried up has no sibling and adds no entry.
- The tree grows as evidence is added. Each version records the root at that moment (section 8).
- An inclusion proof is the list of sibling hashes with a left or right marker. It is the basis of selective disclosure (P1).

### Worked example (illustrative)

Three messages with salts of 16 bytes of `0x01`, `0x02`, `0x03`. The payloads are a simplified four-field message (`id`, `sender`, `text`, `ts`), not the full record of section 4, because the primitives accept any JSON:

| Item | Value |
|---|---|
| Payload 1 (JCS) | `{"id":1,"sender":"Raju","text":"200 shirts, 480 each ok?","ts":"2026-10-12T10:02:00+05:30"}` |
| Leaf 1 | `<generated by scripts/make_test_vectors.py>` |
| Leaf 2 | `<generated by scripts/make_test_vectors.py>` |
| Leaf 3 | `<generated by scripts/make_test_vectors.py>` |
| Node(1,2) | `<generated by scripts/make_test_vectors.py>` |
| Root (node(1,2) with leaf 3 carried up) | `<generated by scripts/make_test_vectors.py>` |

Hash values are not written here by hand. `scripts/make_test_vectors.py` generates them into `test-vectors/integrity/`, and both Python and JavaScript must reproduce them (see section 13 and OPEN_QUESTIONS Q-41). The message text for message 2 is `ok. delivery next week` from Meena, and for message 3 `advance half now` from Raju, both on 12 Oct 2026.

## 7. Echo code

Purpose: let the counterparty confirm a recap by replying with a short code, with nothing to install.

```
recap_hash = H(0x21 || JCS(recap_object))
digest     = H(0x50 || recap_hash)
code_bits  = first 20 bits of digest (big-endian)
code       = 4 characters, 5 bits each, from the Crockford base32 alphabet
             0123456789ABCDEFGHJKMNPQRSTVWXYZ
```

`recap_hash` and `digest` are raw 32-byte values here, not hex text. Reply format: `CONFIRM <code>`.

Normalisation of a pasted reply before comparison: Unicode NFC, upper-case, trim, collapse spaces, map `O` to `0` and `I` or `L` to `1`. The code is searched for after the word `CONFIRM`; other words around it are ignored.

Properties and limits:
- The code is bound to the exact recap text through `recap_hash`. Any change in any line changes the code.
- 20 bits gives about one chance in a million that two different recaps share a code. This is a binding check, not a secret. It does not authenticate the sender.
- The echo code relies on the authenticity of the chat export. VeriDoc stores the reply as evidence (a confirmation leaf, `0x22`).
- A code is valid only for the current recap version. A reply carrying an older version's code is rejected with "this code is for an older version".

## 8. Version chain

```
link_0     = H(0x30 || 32 zero bytes || terms_digest_0 || root_0)
link_n     = H(0x30 || link_(n-1)    || terms_digest_n || root_n)
terms_digest_n = H(0x20 || JCS(terms_set_n))
root_n     = Merkle root at the moment version n was recorded
```

- A version is never edited. A change creates version n+1 whose link includes link_n.
- Changing any earlier terms set, any leaf covered by an earlier root, or any earlier link makes every later link fail verification.
- A confirmation (`0x22` leaf) is added to the tree after the version it confirms; the confirmed state is shown in the next receipt.

## 9. Receipt and bundle

The receipt object (JCS, then `receipt_hash = H(0x40 || JCS(receipt))`):

| Field | Meaning |
|---|---|
| `spec_version` | Version of this specification |
| `deal_id` | Identifier of the deal |
| `leaf_count` | Number of leaves covered |
| `root` | Current Merkle root (hex) |
| `chain` | List of `{version, terms_digest, root, link}` |
| `recorded_at` | Device-clock time |
| `anchor` | Null, or `{network, tx, block_time}` (P1) |

The receipt bundle (`.zip`) contains: `receipt.json`, `leaves.jsonl` (type, salt, payload or payload digest, leaf hash, sequence), `chain.json`, `media/` (audio and attachments, only if exported), `README.txt` (how to verify). Messages in the bundle appear in the original order.

## 10. Verification algorithm

The verify page and the Python verifier implement the same steps and produce the same result. Steps in order:

1. Parse `receipt.json`; check `spec_version` is supported.
2. For each leaf with a payload: recompute `payload_digest` and `leaf`. If a leaf has only a hash, take it as given.
3. Order leaves by sequence and rebuild the Merkle root. Compare with `root`. Record the first leaf whose recomputed hash differs from the listed hash, if any.
4. For each chain entry in order: recompute `terms_digest` and `link`. Compare with the listed values. Record the first link that fails.
5. Check each chain entry's `root` is the root of the tree prefix recorded for that version (leaves with sequence up to that version's last leaf).
6. Check timestamps are in a consistent order (receipt time not earlier than the latest leaf time; version times non-decreasing). Failure is reported as a warning labelled "inconsistent", and counts as ALTERED only if it contradicts the chain.
7. If `anchor` is present, report it as "anchored" with the network and reference. Verifying the anchor transaction needs the network and is outside the offline check; the page says so.
8. Produce the verdict.

Verdict:

| Verdict | Condition |
|---|---|
| ✓ UNCHANGED since recording | Steps 2 to 5 pass. |
| ⚠ ALTERED after recording | Any of steps 2 to 5 fails. Name the first differing item: a leaf (message number, voice-note id, transcript id) or a chain link. |

Order of "first differing item": the lowest leaf sequence number that fails; if all leaves pass, the lowest chain version that fails.

## 11. Tamper cases that must be detected

| # | Case | Expected first differing item |
|---|---|---|
| 1 | One character changed in a message | That message |
| 2 | A message removed | The first leaf after the gap (sequence mismatch) and the root |
| 3 | Two messages swapped | The earlier of the two |
| 4 | Audio file replaced | That voice note's audio leaf |
| 5 | Transcript text changed | That transcript span leaf |
| 6 | An earlier agreement version edited | That chain version |
| 7 | Chain truncated or a version removed | The missing chain link |

Each has a fixture in `test-vectors/integrity/` and a test in Area 3's packages.

## 12. Timestamps and anchoring

- By default the time is the device clock. S8 says so in words.
- P1 optional anchoring writes only the receipt root (or `receipt_hash`) to a public network: Polygon, using the Amoy testnet for the demo. No chat content leaves the device. Anchoring is off by default.
- An anchored root gives an independent "existed no later than" time. It does not change what the hash proves about authenticity.

## 13. Test vectors

`test-vectors/integrity/` holds JSON files written by `scripts/make_test_vectors.py`, which runs the real code. Values are never typed by hand; a test regenerates the files and fails if they differ. Each file lists inputs and expected outputs as lowercase hex (or canonical text), including inputs that must be rejected.

Required groups:
1. SHA-256 sanity: `abc` gives `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
2. JCS edge cases: key order, Unicode (Hindi, Kannada), escapes, the RFC 8785 number table, empty containers, and rejected inputs (integers outside the safe range).
2a. Text normalisation: NFC versus non-NFC input, line endings, keys left alone.
3. Leaves for every salted record type byte, and plain hashes for the others.
4. Merkle trees with 1, 2, 3, 4, 5, 7, 9 and 16 leaves (odd carry-up), their inclusion proofs, and an empty tree (rejected).
5. Version chain of 3 versions.
6. Echo codes including normalisation cases (`o` versus `0`, spaces, lower case).
7. The seven tamper cases in section 11.

Both `packages/integrity/tests/` and the verify page's test run (Node or browser) must load the same files and pass.

## 14. Limits

- Tamper-evident, not proof of authenticity of the original export.
- Device-clock time can be wrong until anchored.
- The echo code is a 20-bit binding check, not authentication.
- Hashes protect integrity, not confidentiality. Confidentiality comes from vault encryption (see [DATA_MODEL](DATA_MODEL.md)).

## 15. Change rule

Any change to hashing, Merkle, version chain, echo code or verify logic must in the same change: update this file, update the test vectors, keep all tamper tests passing, and bump `spec_version` if hashes change.
