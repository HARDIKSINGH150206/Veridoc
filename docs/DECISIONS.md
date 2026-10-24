# Architecture Decision Records

Each record states the context, the decision, the alternatives and the consequences. Status is Accepted for all records below. New decisions are added at the end; a decision is changed by a new record that supersedes the old one, not by editing history.

Last updated: 2026-10-25
Status: Draft v1

| ID | Title |
|---|---|
| ADR-001 | Build from scratch; DigiVault informs design only |
| ADR-002 | LS-06 chosen over the other Legal Services statements |
| ADR-003 | Local-first, offline by default; cloud is opt-in |
| ADR-004 | The pendrive is a delivery vehicle and demo proof, not the product |
| ADR-005 | Python with FastAPI for the backend |
| ADR-006 | SQLite in WAL mode for local storage |
| ADR-007 | Rules first, AI second; AI only suggests and never touches the hash path |
| ADR-008 | llama.cpp with small open models and hardware tiers; no RAG |
| ADR-009 | faster-whisper for voice notes, transcribed at import |
| ADR-010 | Recaps from fixed templates, not free AI text |
| ADR-011 | Echo-code confirmation instead of links or app installs for the counterparty |
| ADR-012 | SHA-256, salted Merkle tree, domain separation, JCS canonicalisation |
| ADR-013 | Tamper-evident wording only |
| ADR-014 | Optional Polygon anchoring for independent timestamps |
| ADR-015 | Static offline verify page in vanilla JavaScript |
| ADR-016 | Playbook-driven generic engine; two playbooks in the MVP |
| ADR-017 | Privacy mask applies to exports, shares and any cloud call, not to local processing |
| ADR-018 | Share link with client-side encryption and the key in the URL fragment |
| ADR-019 | Blind Handshake included as lite MVP with a fallback |
| ADR-020 | Features cut |
| ADR-021 | SQLAlchemy 2.0 with Alembic; no object store in MVP |
| ADR-022 | Router auto-discovery in apps/api/main.py |
| ADR-023 | Optional fine-tuning with an eval gate |

## ADR-001 Build from scratch; DigiVault informs design only

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The team built an earlier project, DigiVault, with a hash-based integrity layer. The hackathon rules and the team's wish to understand every line favour a clean codebase.
- **Decision:** All VeriDoc code is new. DigiVault's design ideas (hash chain, Merkle commitment, offline verify) inform the integrity layer. No DigiVault code, files or data are copied.
- **Alternatives considered:** Reuse DigiVault code; fork DigiVault.
- **Consequences:** More work up front; no hidden legacy issues; ownership is clear. Recorded in PRIOR_WORK.md and README.

## ADR-002 LS-06 chosen over the other Legal Services statements

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Six Legal Services statements were compared (LS-01 to LS-06).
- **Decision:** Build for LS-06, From Handshake to Contract (Informal Agreements). Provable terms are upstream of payment disputes (LS-03) and notice handling (LS-05). It has a wide audience, a real demo and a clear technical edge.
- **Alternatives considered:** LS-05 notice triage (crowded; general chatbots already explain notices); LS-03 MSME payments (narrower, depends on provable terms); LS-01, LS-02, LS-04 (results hard to show in a short demo).
- **Consequences:** All features must trace to LS-06 asks A to F (PRD section 6).

## ADR-003 Local-first, offline by default; cloud is opt-in

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Business chats hold prices, names and bank details. Users often have poor connectivity. Judges can see offline proof.
- **Decision:** All processing runs on the user's device with no network needed. Cloud features (anchoring, share link) are optional modules that send only hashes or ciphertext.
- **Alternatives considered:** Cloud-hosted SaaS from day one; hybrid with cloud AI.
- **Consequences:** No cloud account or subscription. Lower model quality than large cloud models. Network code is confined to two modules.

## ADR-004 The pendrive is a delivery vehicle and demo proof, not the product

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The idea deck sells a portable stick. The product value is the record and the flow, not the hardware.
- **Decision:** Package VeriDoc so it runs from a USB 3 exFAT stick on Windows, macOS and Linux with START.bat or start.sh. The same build also installs on a laptop. Pendrive tiers are the first thing cut after the share link, Blind Handshake and Kannada.
- **Alternatives considered:** Installer only; web hosting only.
- **Consequences:** Portable runtimes add packaging work (Area 1). The product does not depend on the stick.

## ADR-005 Python with FastAPI for the backend

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The team knows Python. The AI, speech and parsing libraries are Python-first. The idea deck left FastAPI or Node open.
- **Decision:** Python 3.11 or later with FastAPI, Pydantic v2 and server-sent events for live analysis. Routes are thin; logic lives in packages.
- **Alternatives considered:** Node with Express; Go.
- **Consequences:** One language for rules, AI and integrity. Portable Python runtimes must be bundled.

## ADR-006 SQLite in WAL mode for local storage

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Needs a single-file, serverless, crash-safe database that lives on a stick.
- **Decision:** One SQLite database per vault in WAL mode with insert-only tables enforced by triggers. Encrypted at the record and file level by the vault layer.
- **Alternatives considered:** Postgres; JSON files; LevelDB.
- **Consequences:** Simple backup (copy a folder). Triggers do not stop direct file edits, so integrity relies on hashes, not on the database. See ADR-021 for the ORM, migrations and evidence files.

## ADR-007 Rules first, AI second; AI only suggests and never touches the hash path

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Small local models make mistakes, and the record must stay trustworthy.
- **Decision:** Deterministic rules run first and show results immediately. A local model refines. Output is schema-constrained and grounded. The AI cannot write to the vault or hash path. A person confirms every term.
- **Alternatives considered:** AI-only extraction; AI auto-confirm.
- **Consequences:** Works without a model (safe mode). More engineering for parsers. Safer evidence.

## ADR-008 llama.cpp with small open models and hardware tiers; no RAG

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Laptops range from 4 GB to 16 GB RAM. No GPU can be assumed. Extraction is schema-driven and needs no retrieval corpus.
- **Decision:** Run open instruction models through llama.cpp (llama-cpp-python) with JSON-schema-constrained output. Pick about 7B, 3B or 1.5B by RAM at startup; safe mode below that. Model files are pinned by SHA-256 in models/manifest.json. Exact models are TBD pending benchmarks. No RAG. Fine-tuning is optional and gated by ADR-023; no fine-tuning claim is made unless it ships.
- **Alternatives considered:** Cloud API; ONNX models; RAG over legal text. (Fine-tuning is handled in ADR-023.)
- **Consequences:** Weaker on Hinglish and Kannada-English; accuracy reported per language. Model benchmark task for Area 2.

## ADR-009 faster-whisper for voice notes, transcribed at import

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Voice notes carry many Indian deals. Live transcription is slower and harder on small laptops.
- **Decision:** Use faster-whisper (small; base on low tiers). Transcribe at import time with a progress indicator. Hash audio and transcript separately. Keep audio for play-the-moment.
- **Alternatives considered:** whisper.cpp (named in the idea deck); live transcription; cloud speech.
- **Consequences:** Python-only stack. Import takes longer for long notes. Transcripts can be wrong, so they are shown with confidence and are correctable.

## ADR-010 Recaps from fixed templates, not free AI text

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** A recap may be relied on later. Free text can invent or soften terms.
- **Decision:** Generate recap text from confirmed terms using fixed per-language templates in playbooks. The AI does not write the recap.
- **Alternatives considered:** AI-written recap; user-written recap.
- **Consequences:** Predictable, reviewable wording, easy native-speaker review. Less natural phrasing.

## ADR-011 Echo-code confirmation instead of links or app installs for the counterparty

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The idea deck used a one-tap link. The counterparty must install nothing and click nothing unfamiliar. The wireframes (S6, S12) show a code reply.
- **Decision:** The recap carries a 4-character code derived from the recap hash. The counterparty replies CONFIRM <code> in WhatsApp. The user pastes the reply and the app verifies it and stores it as evidence.
- **Alternatives considered:** One-tap link (needs a server); OTP via SMS; a counterparty app.
- **Consequences:** Zero friction for the counterparty. The code is a binding check, not authentication, and relies on the export being genuine (stated in LIMITS). Conflict with the idea deck logged.

## ADR-012 SHA-256, salted Merkle tree, domain separation, JCS canonicalisation

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The record must be tamper-evident, checkable offline in a browser, and support selective disclosure later.
- **Decision:** Use SHA-256 with a distinct prefix byte per record type, salted Merkle leaves, a version chain and RFC 8785 JCS before hashing. Python and JavaScript share test vectors.
- **Alternatives considered:** A plain hash of the whole file; a blockchain-only design; SHA-3 or BLAKE3.
- **Consequences:** WebCrypto supports SHA-256 natively. Salts must be stored with the vault. Spec changes need new vectors.

## ADR-013 Tamper-evident wording only

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** A hash cannot stop change; it shows change. Over-claiming would damage trust and could mislead users.
- **Decision:** Use tamper-evident everywhere. State that tamper evidence is not authenticity of the original export. Use court-ready evidence package for the dispute pack, and never describe output as a legal instrument.
- **Alternatives considered:** Stronger marketing wording.
- **Consequences:** Honest claims that survive judge questions. Wording rules are in LIMITS and checked in review.

## ADR-014 Optional Polygon anchoring for independent timestamps

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Device clocks can be wrong. An anchored root gives an independent time.
- **Decision:** P1 optional module anchors the root hash on Polygon (Amoy testnet for the demo). Off by default. Only hashes leave the device.
- **Alternatives considered:** OpenTimestamps; a trusted timestamp authority; no anchoring.
- **Consequences:** Needs the network and a wallet or relayer (TBD). Not in the MVP.

## ADR-015 Static offline verify page in vanilla JavaScript

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** A verifier (lawyer, CA, officer) must check a record without an account, a backend or the internet.
- **Decision:** Ship apps/verify/verify.html as one file using WebCrypto SHA-256, no framework, no CDN. A Python verifier also exists for tests.
- **Alternatives considered:** A hosted verifier; a framework app.
- **Consequences:** Tiny, auditable, works anywhere. Needs a trusted copy of the page (see THREAT_MODEL T19).

## ADR-016 Playbook-driven generic engine; two playbooks in the MVP

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Many deal types share the same shape: required terms, ambiguity rules, hints and templates.
- **Decision:** The engine is deal-agnostic. A YAML playbook defines required terms and weights, ambiguity rules, legal hints, handshake questions and templates. The MVP ships supply or order and freelance or service.
- **Alternatives considered:** Hard-coded logic per deal type; a contract template library (cut).
- **Consequences:** New deal types need data, not code. Playbooks need legal and language review.

## ADR-017 Privacy mask applies to exports, shares and any cloud call, not to local processing

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Local processing needs the real values to work. Risk appears when data leaves the vault.
- **Decision:** Mask bank, card, Aadhaar (with checksum), PAN, IFSC, UPI and OTP or password context on exports, shares and cloud calls. Never mask amounts or dates. Masked parts still verify against the original receipt. P1.
- **Alternatives considered:** Mask everything always; no mask.
- **Consequences:** Local features stay accurate. Mask patterns can miss cases, so a preview is required.

## ADR-018 Share link with client-side encryption and the key in the URL fragment

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Users may want a lawyer or CA to view a record without email attachments.
- **Decision:** P1 share link: the bundle is encrypted on the device, the key lives in the URL fragment so the server never sees it, view-only, with expiry, revoke and an access log. The first feature in the drop order.
- **Alternatives considered:** Plain hosted link; email attachments.
- **Consequences:** Needs an optional share server. Link forwarding cannot be prevented.

## ADR-019 Blind Handshake included as lite MVP with a fallback

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** Misunderstandings often show only after work starts. A sealed answer exchange exposes them early and feels like a friendly check.
- **Decision:** Both sides answer 3 to 4 key questions privately. Answers are hashed and timestamped, then revealed side by side. Reply mode is the primary mode (the user seals first, then the counterparty answers in a WhatsApp reply that the user pastes); handover mode is the demo mode. In both, the first party's answers must be sealed before the second can submit. If time is short or the counterparty cannot take part, fall back to a plain recap. Second in the drop order.
- **Alternatives considered:** Skip it; build in-person voice sealing (roadmap).
- **Consequences:** Extra UI and state machine. Blindness is procedural in the lite version and is labelled as such.

## ADR-020 Features cut

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The scope must be defendable and finished.
- **Decision:** Cut: counterparty reliability scores, fake-chat detection claims, verdict prediction, contract template library, full payment ledger, late-interest calculator, formal-notice escalation, fine-tuning claims that are not backed by an eval gate (ADR-023), RAG. Reasons: they cannot be validated, drift into legal practice, or are outside LS-06.
- **Alternatives considered:** Keep a subset as stretch goals.
- **Consequences:** A tighter story. Each is listed in PRD non-goals so nobody builds it by accident.

## ADR-021 SQLAlchemy 2.0 with Alembic; no object store in MVP

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** The vault needs typed database access, a versioned schema across four people's work, and insert-only audit rules that survive refactors. Evidence files (audio, attachments) must stay private and verifiable. A cloud tier may later need shared storage.
- **Decision:** Use SQLAlchemy 2.0 for database access and Alembic for migrations. The insert-only audit triggers live in an Alembic migration as raw SQL. Evidence files are stored in an encrypted local folder, each named by its hash. MinIO or any S3-compatible store is roadmap only, for the cloud tier's share bundles.
- **Alternatives considered:** Raw `sqlite3` with hand-written schema scripts; an ORM without migrations; storing audio as database blobs; an object store from day one.
- **Consequences:** Two more dependencies, owned by the dependency owner. Schema changes need a migration and a trigger check in tests. File names reveal content hashes (THREAT_MODEL T29). No server to run in the MVP. Area 3 owns the migrations in `packages/vault/migrations/`.

## ADR-022 Router auto-discovery in apps/api/main.py

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** `apps/api/main.py` is a hotspot owned by Area 3 (Jhashank). If every new route needed an edit there, three other areas would queue for one file and conflict often.
- **Decision:** `main.py` loads every module in `apps/api/routers/` automatically. Each module exposes one router object by a fixed name. Adding a route means editing only the router file in your own area. Nobody edits `main.py` to add a route.
- **Alternatives considered:** Explicit imports in `main.py`; one router per area registered by hand; a plugin entry-point system.
- **Consequences:** A new router file is picked up with no other change. A broken router module is reported at startup by name rather than silently skipped. Router modules must be import-safe (no work at import time). Area 3 writes the loader in Phase 0.

## ADR-023 Optional fine-tuning with an eval gate

- **Status:** Accepted
- **Date:** 2026-10-25
- **Context:** An earlier decision said we make no fine-tuning claim. A small model fine-tuned on Indian informal-deal chats (Hinglish, Kannada-English) might beat the base model on our fields, but we cannot know until we measure. The team has an AI and ML owner who can run it. A claim without a measurement would damage trust.
- **Decision:** Fine-tuning (for example LoRA) is a P1 task owned by Abhishek (Area 2). It is shipped, and claimed in any document, slide or answer, only if the fine-tuned model beats the base model of the same tier on the held-out eval split. Gate:
  1. Field-level F1 on the held-out split is higher than the base model's by at least a margin (value TBD, OPEN_QUESTIONS Q-50).
  2. No regression on grounding failures, prompt-injection fixtures, needs-review rate or any language slice beyond a tolerance (TBD, Q-50).
  3. Training data is synthetic or consented, contains none of the eval or held-out chats, and is recorded in the DATASET_CARD.
  4. The base model's and the fine-tuned model's licences allow our use and redistribution (Q-46).
  5. The fine-tuned file is pinned by SHA-256 in `models/manifest.json`; weights are never committed.
  6. Results, data description and limits are written in MODEL_CARD.md before shipping.
  If the gate is not met, the base model ships and no fine-tuning claim is made. All other safeguards (grounding, human confirmation, safe mode) apply unchanged.
- **Alternatives considered:** Never fine-tune; fine-tune and claim without a gate; fine-tune in the MVP.
- **Consequences:** Extra work after the MVP (Phase 5). The base-model path stays the default and must always work. The eval set must stay clean: no tuning on the held-out split.
