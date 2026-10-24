# Glossary

Plain-language definitions of the terms used in VeriDoc documents.

Last updated: 2026-10-25
Status: Draft v1

| Term | Meaning |
|---|---|
| Acknowledged by both | The other party agreed to a term in the chat, or confirmed a recap that contains it |
| Ambiguous | A value exists but cannot be relied on, such as "next week" |
| Anchoring | Writing a hash to a public network so its time does not depend on one device clock (P1, optional) |
| Argon2id | A password-based key derivation function that makes guessing a passphrase slow |
| Audit table | A table of events that can only be added to, never changed or deleted |
| BSA | Bharatiya Sakshya Adhiniyam, India's evidence law; Section 63 deals with electronic records (a lawyer must confirm how it applies) |
| Blind Handshake | Both sides answer key questions privately, answers are sealed, then revealed side by side |
| Chat recommendation | The one suggested next message that closes the biggest gap |
| Commitment | The Merkle root that stands for all records in a deal |
| Conflict | Two different values for one term |
| Contracts (package) | Shared Pydantic schemas used by every area |
| Counterparty | The other side of the deal; installs nothing |
| Crypto-shredding | Deleting data by deleting its encryption key |
| Device clock | The time on the user's computer; can be wrong |
| Dispute pack | An export with timeline, evidence index, versions, verification guide and draft certificate; a court-ready evidence package |
| Domain separation | A distinct prefix byte for each record type so hashes cannot be mixed up |
| DPDP | India's Digital Personal Data Protection law; a lawyer must confirm duties |
| Echo code | A 4-character code derived from the recap's hash; the counterparty replies CONFIRM and the code |
| Evidence Strength | A 0 to 100 score showing how provable a deal is today |
| Eval set | The labelled chats used to measure accuracy |
| faster-whisper | The local speech-to-text engine |
| Grounding | Checking that an AI value appears in a real message or transcript |
| Hash | A fixed-length fingerprint of data; any change gives a different hash |
| Hinglish | Hindi and English mixed in one message |
| JCS | JSON Canonicalization Scheme (RFC 8785), a fixed way to write JSON before hashing |
| Leaf | The hash of one record in the Merkle tree |
| llama.cpp | The local engine that runs the language model |
| Merkle tree | A tree of hashes whose root commits to every leaf |
| MSME Facilitation Council | A body that handles payment disputes for micro and small enterprises (a lawyer must confirm scope) |
| Needs review | A term marked for a person to check, for example when rules and AI disagree |
| Paper Seal | A QR code on a paper document that opens the verify page (P1) |
| Playbook | A file defining a deal type: required terms, ambiguity rules, hints and templates |
| Privacy mask | Replacing sensitive items such as account numbers in exports (P1) |
| Receipt | The tamper-evident record: chain, root, time and bundle |
| Recap | The short plain-language summary the counterparty confirms |
| Recovery key | A printed key that opens the vault if the passphrase is lost |
| Rules engine | Deterministic code that finds amounts, dates and phrases |
| Safe mode | Rules-only mode with no AI model |
| Salt | Random data added before hashing so contents cannot be guessed |
| Selective disclosure | Sharing only chosen messages while the record still verifies (P1) |
| Share link | An encrypted view-only link with the key in the URL fragment (P1) |
| SSE | Server-sent events; the one-way stream used for live analysis |
| Tamper-evident | A change after saving can be detected; it is not prevented |
| Term | One agreed fact in a deal, such as price or delivery date |
| Trust report | A generated report of measured accuracy and safety results |
| Vault | The encrypted local storage for a user's deals |
| Verify page | A standalone offline page that checks a receipt bundle |
| Verifier | Anyone checking a record: a lawyer, CA, council officer or judge |
| Version chain | Each agreement version includes the hash of the previous one |
| WAL | Write-ahead logging, a crash-safe SQLite mode |
