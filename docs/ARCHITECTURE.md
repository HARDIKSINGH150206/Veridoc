# Architecture

This document describes how VeriDoc is built: system context, containers, components, key sequences, trust boundaries, deployment, technology, folders, API, errors, configuration, logging and the path to production. The code does not exist yet; this is the design the team builds to.

Last updated: 2026-10-25
Status: Draft v1

Related: [PRD](PRD.md), [INTEGRITY_SPEC](INTEGRITY_SPEC.md), [AI_SPEC](AI_SPEC.md), [DATA_MODEL](DATA_MODEL.md), [DECISIONS](DECISIONS.md), [THREAT_MODEL](THREAT_MODEL.md).

## 1. System context

The primary user runs VeriDoc on a laptop. The counterparty uses only WhatsApp. A verifier opens the verify page. Anchoring and share link are optional and off by default.

```mermaid
flowchart LR
  U["Primary user"] --> V["VeriDoc on laptop or USB stick"]
  V -->|"user copies recap text"| WA["WhatsApp"]
  WA --> CP["Counterparty, installs nothing"]
  CP -->|"replies CONFIRM code"| WA
  WA -->|"user exports chat, pastes reply"| V
  V -->|"receipt bundle or dispute pack"| VER["Verifier: lawyer, CA, council, judge"]
  VER --> VP["verify.html, offline"]
  V -.->|"optional P1: hash only"| ANC["Anchoring network"]
  V -.->|"optional P1: ciphertext only"| SRV["Share server"]
```

VeriDoc never connects to WhatsApp. All exchange with WhatsApp is by the user copying text and exporting chats.

## 2. Container view

```mermaid
flowchart TB
  subgraph Launcher["Launcher: START.bat and start.sh"]
    L["Tier detection, starts API, opens browser"]
  end
  subgraph Device["Local device"]
    UI["Browser UI: static HTML and JS, bundled fonts"]
    API["Local FastAPI backend on 127.0.0.1"]
    RULES["Rules engine"]
    AI["AI runner: llama.cpp"]
    SPEECH["Speech runner: faster-whisper"]
    INT["Integrity engine"]
    DB[("SQLite vault via SQLAlchemy 2.0 and Alembic, WAL")]
    FILES[("Encrypted evidence folder, files named by hash")]
    VPAGE["verify.html standalone"]
  end
  L --> API
  L --> UI
  UI <-->|"HTTP and server-sent events"| API
  API --> RULES
  API --> AI
  API --> SPEECH
  API --> INT
  API --> DB
  API --> FILES
  INT --> DB
  VPAGE -. "reads exported bundle only" .- INT
```

| Container | Responsibility | Owner |
|---|---|---|
| Launcher | Detect hardware tier, start the API, open the browser | Area 4 |
| Browser UI | Screens S1 to S12, built against mock data matching contracts | Area 4 |
| Local API | Thin routes, SSE streams, no business logic | Areas 1 to 4 (per router) |
| Rules engine | Deterministic parsers, flags, score, suggestion text | Area 2 |
| AI runner | Local model refinement with schema-constrained output | Area 2 |
| Speech runner | Voice-note transcription at import | Area 1 |
| Integrity engine | Hashing, Merkle, version chain, echo code, anchoring | Area 3 |
| Vault | SQLite through SQLAlchemy 2.0, Alembic migrations, encryption, audit table, encrypted evidence folder, dispute pack | Area 3 |
| Verify page | Standalone offline check | Area 3 |

## 3. Component view of the backend

```mermaid
flowchart TB
  subgraph Routers["apps/api/routers"]
    R1["ingest.py"]
    R2["analysis.py"]
    R3["vault.py"]
    R4["export.py"]
  end
  subgraph Contracts["packages/contracts"]
    CT["Pydantic schemas"]
  end
  subgraph Ingest["packages/ingest"]
    P["WhatsApp parser"]
    M["Media handler"]
    V["Voice transcriber"]
    RC["Recap builder"]
    HS["Blind Handshake logic"]
  end
  subgraph Intel["packages/intelligence"]
    RU["Rules"]
    LM["Local AI and grounding"]
    FL["Flags"]
    SC["Score"]
    SG["Suggestion"]
    PB["Playbook loader"]
  end
  subgraph Integ["packages/integrity"]
    HA["Hashing and JCS"]
    MK["Merkle"]
    VC["Version chain"]
    EC["Echo code"]
    AN["Anchoring, P1"]
  end
  subgraph Vault["packages/vault"]
    ST["SQLAlchemy store and Alembic migrations"]
    EN["Encryption"]
    AU["Audit table"]
    DP["Dispute pack"]
  end
  R1 --> Ingest
  R2 --> Intel
  R3 --> Integ
  R3 --> Vault
  R4 --> Vault
  Ingest --> CT
  Intel --> CT
  Integ --> CT
  Vault --> CT
  Vault --> Integ
```

Dependency rules:
1. Packages depend on `packages/contracts` and on nothing else shared.
2. `packages/intelligence` must not import `packages/vault` or the hashing functions of `packages/integrity` (the AI cannot reach the hash path).
3. Only `packages/vault` writes to the database.
4. Routers call packages and contain no logic.
5. Network calls exist only in the anchoring and share modules.

## 4. Sequence: import to receipt

```mermaid
sequenceDiagram
  actor U as Primary user
  participant UI as Browser UI
  participant API as Local API
  participant ING as Ingest
  participant INT as Intelligence
  participant VLT as Vault and Integrity
  actor CP as Counterparty on WhatsApp
  U->>UI: Choose export file
  UI->>API: POST preview
  API->>ING: Parse text and media
  ING-->>UI: Preview with counts and participants
  U->>UI: Pick which one is you, Analyse
  UI->>API: POST commit
  API->>VLT: Store messages and voice notes, hash leaves
  API->>ING: Transcribe voice notes
  API->>INT: Analyse
  INT-->>UI: Rules terms and flags (stream)
  INT-->>UI: AI refined terms, needs review (stream)
  U->>UI: Confirm or correct terms
  UI->>API: POST confirm
  API->>INT: Score and suggestion
  INT-->>UI: Score and next message
  U->>CP: Pastes suggested message in WhatsApp
  U->>UI: Build recap
  UI->>API: POST recap
  API->>ING: Fill templates from confirmed terms
  API->>VLT: Create version, recap hash, echo code
  VLT-->>UI: Recap text and code
  U->>CP: Pastes recap in WhatsApp
  CP-->>U: CONFIRM code
  U->>UI: Paste reply
  UI->>API: POST check reply
  API->>VLT: Verify code, store reply as leaf, update chain
  VLT-->>UI: Confirmed
  UI->>API: GET receipt
  VLT-->>UI: Root, chain, timestamp
```

## 5. Sequence: verification

```mermaid
sequenceDiagram
  actor V as Verifier
  participant B as Browser with verify.html
  participant S as Share server (P1, optional)
  alt Offline bundle
    V->>B: Open verify.html, drop bundle zip
  else Share link (P1)
    V->>B: Open link with key in fragment
    B->>S: Fetch ciphertext (no key sent)
    S-->>B: Ciphertext
    B->>B: Decrypt in browser
  end
  B->>B: Rebuild leaf hashes (WebCrypto SHA-256)
  B->>B: Rebuild Merkle root and compare
  B->>B: Recompute version chain and compare
  B->>B: Check timestamp order and anchor field
  B-->>V: UNCHANGED, or ALTERED with first differing item
  Note over B,V: Limit shown: not proof the export was genuine
```

## 6. Data flow and trust boundaries

```mermaid
flowchart LR
  subgraph Untrusted["Untrusted input"]
    F["Chat files, zip, audio"]
    T["Chat text"]
  end
  subgraph DeviceB["Device boundary"]
    subgraph Proc["Processing"]
      PARSE["Parse"]
      RULE["Rules"]
      MODEL["Local model"]
    end
    CONF["Human confirmation"]
    subgraph Trusted["Hash path and vault"]
      HASH["Integrity engine"]
      STORE[("Encrypted vault")]
    end
  end
  subgraph Out["Leaves the device by user action"]
    BUN["Receipt bundle or dispute pack"]
  end
  subgraph Net["Optional network"]
    A["Anchoring: hash only"]
    SH["Share server: ciphertext only"]
  end
  F --> PARSE
  T --> RULE
  PARSE --> RULE
  RULE --> MODEL
  MODEL -->|"proposals only"| CONF
  RULE --> CONF
  CONF --> HASH
  HASH --> STORE
  STORE --> BUN
  HASH -.-> A
  BUN -.-> SH
```

Rule: the arrow from the model goes only to human confirmation. Nothing from the model reaches the hash path.

## 7. Deployment view

```mermaid
flowchart TB
  subgraph Stick["MVP: USB 3 stick, exFAT"]
    S1["START.bat, start.sh"]
    S2["Portable Python runtime"]
    S3["App code, bundled web assets"]
    S4["Model files (hash-checked)"]
    S5["Encrypted vault folder: SQLite plus evidence files"]
  end
  subgraph Laptop["MVP alternative: laptop install"]
    L1["Same build in a local folder"]
  end
  subgraph Future["Roadmap"]
    F1["Installable phone web app"]
    F2["Android app: Share to VeriDoc"]
    F3["Cloud tier: sync, teams, billing"]
  end
  Stick --> Laptop
  Laptop -.-> F1
  F1 -.-> F2
  F2 -.-> F3
```

Windows, macOS and Linux runtimes ship side by side on the stick. The stick is a delivery vehicle and demo proof; the product does not depend on it.

## 8. Technology

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2 | One language for rules, AI and integrity; typed I/O |
| Live updates | Server-sent events | One-way stream is enough; simple |
| Rules | `re`, `dateparser`, `rapidfuzz` plus custom parsers | Fast, deterministic, explainable |
| Local AI | llama.cpp via `llama-cpp-python`, small open instruction models, JSON-schema output | CPU-friendly, offline, valid structured output |
| Speech | faster-whisper (small; base on low tiers) | Good Hindi and English accuracy for size; Python |
| Storage | SQLite WAL | Single file, crash-safe, no server |
| ORM and migrations | SQLAlchemy 2.0, Alembic | Typed models; versioned schema; insert-only triggers shipped as raw SQL in a migration (ADR-021) |
| Evidence files | Encrypted local folder, files named by hash | No object store needed on one device; content-addressed |
| Object store (roadmap) | MinIO or any S3-compatible store | Only for the cloud tier's share bundles; not in the MVP |
| Encryption | AES-GCM, Argon2id | Standard, reviewed primitives |
| Integrity | SHA-256, salted Merkle, domain separation, RFC 8785 JCS | Offline verify with WebCrypto; cross-language |
| Anchoring (P1) | Polygon, Amoy testnet in the demo | Cheap independent timestamp; hash only |
| Frontend | Static HTML and JavaScript, no CDN | Works offline; no build step needed at demo time |
| Verify page | Vanilla JavaScript, WebCrypto | Auditable single file |
| PDF | fpdf2 with uharfbuzz, or browser rendering (decision TBD) | Correct Indic shaping |
| Packaging | Portable runtimes; START.bat and start.sh; exFAT | No installer or admin rights |
| Quality | pytest, ruff, mypy, gitleaks, pip-audit, pre-commit | Catch errors and secrets early |

## 9. Folder structure and owners

This matches the repository skeleton and CODEOWNERS exactly.

```
Veridoc/
├── apps/
│   ├── api/                    FastAPI app, thin layer of routes only
│   │   ├── main.py             registers routers; hotspot, Area 4 only
│   │   └── routers/
│   │       ├── ingest.py       Area 1
│   │       ├── analysis.py     Area 2
│   │       ├── vault.py        Area 3
│   │       └── export.py       Area 3
│   ├── web/                    Area 4
│   │   ├── components/         shared UI pieces, Area 4 only
│   │   ├── screens/            one folder per screen: s1-deals ... s12-whatsapp
│   │   └── assets/             bundled CSS, JS and Indic fonts, no CDN
│   └── verify/                 standalone verify.html, Area 3
├── packages/
│   ├── contracts/              shared Pydantic schemas, the ONLY shared code
│   ├── ingest/                 Area 1: WhatsApp parser, media, voice, recap builder, Blind Handshake logic
│   ├── intelligence/           Area 2: rules, local AI, flags, score, suggestion
│   ├── integrity/              Area 3: hashing, Merkle, version chain, echo code, anchoring
│   └── vault/                  Area 3: SQLite, encryption, audit table, dispute pack
├── playbooks/                  Area 2: supply_order.yaml, freelance.yaml
│   └── templates/              Area 1: recap and suggestion templates (en/, hi/)
├── eval/                       Area 2: chats/, labels/, runner/, reports/ (git-ignored)
├── test-vectors/integrity/     Area 3: hashes that Python and JS must both match
├── packaging/                  Area 4: START.bat, start.sh, portable runtimes, tier detection
├── models/manifest.json        model names and SHA-256 only, never weights
├── scripts/                    trust report and dev helpers
├── docs/                       each document has an owner listed in TEAM_GUIDE
├── changes/                    changelog fragments, one file per pull request
├── .github/                    CODEOWNERS, pull_request_template.md, ISSUE_TEMPLATE/, workflows/
├── pyproject.toml + uv.lock    dependency owner only
├── CHANGELOG.md               combined from changes/ at phase end by the release lead
├── .gitattributes              line endings (LF) and binary file rules
├── .gitignore                  Python, Node, OS, secrets, weights, reports, real chats
├── .editorconfig               indentation and final newline rules
├── CLAUDE.md
├── AGENTS.md
└── README.md
```

Each package has its own `tests/` folder inside it. There is no shared top-level tests folder. Alembic migrations live inside `packages/vault/migrations/` (Area 3), so they add no new top-level folder. Each package keeps its fixtures in its own `fixtures/` folder (created by the owning area when needed). `apps/api/main.py` loads every module in `apps/api/routers/` automatically (ADR-022), so adding a route never touches `main.py`. The design tokens live in one file, `apps/web/assets/design-tokens.css` (Area 4).

| Area | Owns | Role |
|---|---|---|
| 1. Ingest, Voice and Agreement | `packages/ingest`, `apps/api/routers/ingest.py`, `playbooks/templates/`, sample chats | Ingest and agreement lead |
| 2. Intelligence | `packages/intelligence`, `playbooks/` (except `playbooks/templates/`), `eval/`, `apps/api/routers/analysis.py` | AI and rules lead |
| 3. Integrity and Vault | `packages/integrity`, `packages/vault`, `apps/verify`, `test-vectors/`, `apps/api/routers/vault.py`, `apps/api/routers/export.py` | Integrity lead |
| 4. Frontend and Packaging | `apps/web`, `packaging/`, `apps/api/main.py` | UI and release lead |

Shared by all, changed only by small reviewed pull requests: `packages/contracts`, `docs/`, `.github/`. Dependency files (`pyproject.toml`, `uv.lock`) have one named owner (TBD).

## 10. API overview

All routes are under `/api`, bind to 127.0.0.1, require the session token header once the vault is unlocked, and return JSON using contract models. Paths are indicative; the contracts package is the source of truth.

| Router | Method and path | Request | Response |
|---|---|---|---|
| vault | `POST /vault/setup` | passphrase | recovery key (once) |
| vault | `POST /vault/unlock` | passphrase or recovery key | session token |
| vault | `POST /vault/lock` | none | ok |
| ingest | `GET /ingest/samples` | none | sample list |
| ingest | `POST /ingest/preview` | file or pasted text | counts, participants, date range, warnings |
| ingest | `POST /ingest/commit` | preview id, which-one-is-you, parties, deal type, date order | deal id |
| ingest | `POST /deals/{id}/messages` | simulator message | message |
| ingest | `GET /deals/{id}/voice/{vid}/audio?start=&end=` | none | audio clip for play-the-moment |
| vault | `GET /deals` | filter | deal summaries |
| analysis | `GET /deals/{id}/analysis/stream` | none | SSE: terms, flags, score, suggestion |
| analysis | `POST /deals/{id}/terms/{key}/confirm` | value | term |
| analysis | `POST /deals/{id}/terms/{key}/correct` | value | term, audit event |
| analysis | `POST /deals/{id}/terms/{key}/reject` | none | term |
| analysis | `GET /deals/{id}/suggestion?tone=` | none | suggestion |
| ingest | `POST /deals/{id}/handshake/start` | none | questions |
| ingest | `POST /deals/{id}/handshake/answers` | party, answers | seal record (refused until the first set is sealed) |
| ingest | `POST /deals/{id}/handshake/reveal` | none | side-by-side result |
| ingest | `POST /deals/{id}/recap` | language | recap text, lines, code |
| vault | `POST /deals/{id}/recaps/{rid}/check-reply` | pasted text, sender | confirmation state |
| vault | `GET /deals/{id}/versions` and `/versions/diff?a=&b=` | none | versions, diff |
| vault | `GET /deals/{id}/receipt` | none | receipt |
| export | `POST /deals/{id}/export/bundle` | none | bundle file |
| export | `POST /deals/{id}/export/pack/preview` | parts | PDF preview, size |
| export | `POST /deals/{id}/export/pack` | parts | pack file |
| main | `GET /health` | none | self-check results, tier, model status |
| main | `GET` and `POST /settings` | settings | settings (language, safe mode, anchoring) |

## 11. Error handling strategy

| Rule | Detail |
|---|---|
| Typed errors | Packages raise typed errors; routers map them to one error body: `{code, message_en, message_hi, hint}` |
| Plain messages | The UI shows the message and hint, not stack traces |
| Fail safe | Model errors fall back to rules; transcription errors keep the audio and mark "not transcribed" |
| No partial records | Imports and versions are one transaction; failure leaves nothing half-written |
| Integrity errors | A hash mismatch is never swallowed; it is shown as ALTERED or as a self-check failure |
| Retries | No automatic retries on writes; the user retries |
| No content in errors | Error messages and logs hold no chat content or identifiers |
| Timeouts | Every AI and speech call has a timeout; the rules result stands |

## 12. Configuration and environment

Names only. Values live in a local `.env` (never committed) or in the launcher; `.env.example` lists the names.

| Name | Purpose |
|---|---|
| `VERIDOC_HOME` | Folder for the vault and logs |
| `VERIDOC_PORT` | Local port (default chosen at start) |
| `VERIDOC_TIER` | Force a hardware tier |
| `VERIDOC_SAFE_MODE` | Force rules-only mode |
| `VERIDOC_MODEL_DIR` | Folder holding model files |
| `VERIDOC_MANIFEST_PATH` | Path to `models/manifest.json` |
| `VERIDOC_MAX_IMPORT_MB` | Import size cap |
| `VERIDOC_LOG_LEVEL` | Log level |
| `VERIDOC_FEATURE_FLAGS` | Comma-separated names of unfinished features to switch on (see DEVELOPMENT_METHODOLOGY) |
| `VERIDOC_ANCHOR_ENABLED` | Enable anchoring (P1; default off) |
| `VERIDOC_ANCHOR_RPC` | Anchoring network endpoint (P1) |
| `VERIDOC_SHARE_BASE_URL` | Share server base (P1) |

No secret is ever a default value in code.

## 13. Logging rules

1. Log events, counts, durations and error codes only.
2. Never log message text, transcripts, names, phone numbers, term values, passphrases, keys or file names from the user.
3. Use stable event names (`import_committed`, `model_loaded`, `safe_mode_on`).
4. Log rotation at a small fixed size; logs stay in `VERIDOC_HOME`.
5. A test greps captured logs for fixture strings.

## 14. Path to production

| Stage | Work |
|---|---|
| After the hackathon | Fix what the trust report shows; real pilot with 5 to 10 small businesses; lawyer review of wording, certificate and DPDP; Hindi and Kannada native review |
| Hardening | Signed releases; reproducible builds; third-party security review of vault and integrity; fuzzing of parsers |
| Product | Installable phone web app, then Android "Share to VeriDoc"; better voice; more playbooks |
| Services | Optional cloud tier (this is where an S3-compatible store such as MinIO enters, for share bundles): encrypted sync, teams, billing, CA or lawyer review marketplace; WhatsApp extension; anchoring service |
| Compliance | DPDP notices and consent for counterparty data; retention policy; incident process |

The integrity format is versioned (`spec_version`) so older receipts stay verifiable as the product grows.
