# Open Questions

Every `TBD` in the repository, and every conflict found between the source documents, is recorded here. Owners were assigned on 2026-10-25 from the area table in TEAM_GUIDE (Samanway Area 1, Abhishek Area 2, Jhashank Area 3, Hardik Area 4 and project-wide or legal items). Jhashank's items are covered by Hardik until the repository invitation is accepted. When a question is answered, move it to the "Resolved" table with the date and the document changed.

Last updated: 2026-10-25
Status: Draft v1

## 1. Conflicts between sources

The ground rule is: this prompt wins, then `docs/source/VeriDoc-Final-Idea.md`, then `docs/source/veridoc-wireframes.html`. These conflicts were found while writing the first draft.

| ID | Conflict | Sources | Resolution used | Owner |
|---|---|---|---|---|
| C-05 | Model: idea names Qwen2.5 7B Q4 with 3B fallback; master prompt says model choices are TBD with hardware tiers (7B, 3B, 1.5B, safe mode) | Idea section 7 | Tiers, models TBD pending benchmarks | Abhishek |
| C-06 | Backend: idea says "Python FastAPI or Node"; master prompt fixes Python | Idea section 7 | Python, FastAPI | Jhashank |
| C-07 | Frontend: idea says static HTML, JS and Tailwind; master prompt requires bundled assets with no CDN | Idea section 7 | Bundled CSS and JS, no CDN; whether Tailwind is used as a build-time tool is Area 4's choice | Hardik |
| C-08 | Prior work: idea says the integrity layer is "reused from our earlier DigiVault design"; master prompt says build from scratch with no code reuse | Idea section 7 | From scratch; design ideas only (PRIOR_WORK) | Hardik |
| C-09 | Anchoring: the idea document lists blockchain anchoring as roadmap; master prompt makes optional anchoring P1 | Idea section 4; wireframe S8 (P1) | P1 | Hardik |
| C-10 | Deal types: wireframe S2 shows only supply or order enabled and "Freelance job, later"; master prompt ships two playbooks in the MVP | Wireframe S2 | Two playbooks in the MVP | Abhishek |
| C-12 | Dispute-readiness view ("here is what you could prove today") appears as an add-on in the idea document and is not in the master prompt's feature list | Idea section 4 | Not built; Evidence Strength score covers the need | Hardik |
| C-13 | Idea document says a pendrive of 16 GB; master prompt says USB 3 stick, exFAT, without a size | Idea sections 3, 6 | USB 3, exFAT; size TBD | Samanway |
| C-14 | Wireframe S12 and S6 mention the word "fingerprint" for the hash; master prompt uses "hash" | Wireframe S6 | UI may use "fingerprint" as plain-language copy; docs use "hash" | Hardik |
| C-15 | The idea document calls the stick "encrypted vault ... Eject" in its header wireframe; the PRD does not specify an Eject control | Idea section 5 | Optional UI control; Area 4 decides | Hardik |

## 2. Open items

### Product and legal

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-01 | Product owner, engineering owners and legal reviewer names | PRD section 1 | Hardik |
| Q-02 | Lawyer review of every statement about Indian law, including whether and how chat agreements may be valid contracts | PRD section 13, JUDGE_QA | Hardik |
| Q-03 | Which deal types need a written, stamped or registered document, and the exact legal-hint wording | PLAYBOOKS | Hardik |
| Q-04 | Form and applicability of the draft Section 63 BSA certificate for chat evidence | PRD FR-DSP-003 | Jhashank |
| Q-05 | DPDP: lawful basis, notice and consent for the counterparty's data; counterparty deletion requests; breach process | PRIVACY section 8 | Hardik |
| Q-06 | Legal retention period for deal records | DATA_MODEL section 6, PRD section 11 | Jhashank |
| Q-07 | Stamp-duty hints: which one or two states, and verified figures (P1) | PRD FR-STP-001 | Abhishek |
| Q-08 | Licence of the repository | README | Hardik |
| Q-09 | Whether DigiVault's repository is public | PRIOR_WORK | Hardik |
| Q-10 | Hackathon event name, date, venue and any rules that affect scope | DEMO_SCRIPT, ROADMAP | Hardik |
| Q-11 | Calendar dates for build phases | ROADMAP | Hardik |
| Q-12 | Revenue model hypotheses to validate | ROADMAP section 5 | Hardik |

### AI, language and evaluation

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-13 | Exact extraction models per tier (about 7B, 3B, 1.5B), chosen by benchmark | AI_SPEC, PERFORMANCE, DECISIONS ADR-008, manifest | Abhishek |
| Q-14 | Speech models (small, base) and versions | AI_SPEC, manifest | Abhishek |
| Q-15 | Voice-segment confidence threshold for "needs review" | AI_SPEC section 7, PRD FR-VOI-003 | Abhishek |
| Q-16 | Per-language accuracy targets (Hinglish, Kannada-English) after the first trust report | EVALUATION section 4 | Abhishek |
| Q-17 | Native-speaker review of Hindi templates and limits wording | PLAYBOOKS, LIMITS | Samanway |
| Q-18 | Native-speaker review of Kannada templates (P1) | PRD FR-KAN-001 | Samanway |
| Q-19 | Eval set labellers and the reviewer roster | EVALUATION section 2 | Abhishek |
| Q-20 | Trust report command name and location | EVALUATION section 6, SETUP | Jhashank |

### Integrity and security

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-21 | Final domain-separation byte values and field lists, fixed by test vectors | INTEGRITY_SPEC | Jhashank |
| Q-22 | Echo-code length (4 characters, 20 bits) is enough, or should it be longer | INTEGRITY_SPEC section 7 | Jhashank |
| Q-23 | Argon2id parameters tuned for 8 GB laptops | DATA_MODEL section 5 | Jhashank |
| Q-24 | Maximum import size and archive limits | PRD FR-IMP-002, ARCHITECTURE section 12 | Samanway |
| Q-26 | Anchoring: relayer or wallet approach and cost for Polygon Amoy (P1) | DECISIONS ADR-014 | Hardik |
| Q-27 | Signed releases and publication of the verify page hash | THREAT_MODEL T19 | Hardik |
| Q-28 | Security contact address and response timelines | SECURITY | Hardik |

### Engineering and packaging

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-34 | PDF renderer: fpdf2 with uharfbuzz, or browser rendering | ARCHITECTURE section 8 | Jhashank |
| Q-35 | Tier detection rule for "old CPU" | PERFORMANCE section 1 | Abhishek |
| Q-36 | The three benchmark laptops | PERFORMANCE section 4 | Samanway |
| Q-37 | All install, run, test, lint, type-check, trust-report and pendrive-build commands | SETUP, CLAUDE.md, AGENTS.md | Hardik |
| Q-38 | Whether Tailwind is used as a build-time tool (output must still be bundled with no CDN) | Conflict C-07 | Hardik |
| Q-39 | Demo roles: presenter, second person, operator | DEMO_SCRIPT | Hardik |
| Q-40 | Confirmation-rate, time-to-confirm and score-improvement baselines from a pilot | PRD section 15 | Samanway |
| Q-41 | Generate real test vectors with a script; Python and JS must both reproduce them. | INTEGRITY_SPEC sections 6 and 13 | Jhashank |
| Q-42 | User research: who interviews, participant mix and the notes folder | USER_RESEARCH section 3 | Samanway |
| Q-43 | Team chat platform (the project board exists: https://github.com/users/HARDIKSINGH150206/projects/1; make it public or add collaborators) | ONBOARDING sections 4 and 14 | Hardik |
| Q-44 | Who owns GitHub repository settings (branch protection, merge settings, tag protection) | GIT_WORKFLOW section 7 | Hardik |
| Q-45 | Where security incidents (such as a pushed secret) are recorded | ONBOARDING section 21 | Hardik |
| Q-46 | Licence check of each chosen model for redistribution on a USB stick | MODEL_CARD | Abhishek |
| Q-47 | When to raise required approvals from 0 to 1 (proposed: start of Phase 1), turn on code-owner review and include administrators (proposed: before the demo) | GIT_WORKFLOW section 7 | Hardik |
| Q-48 | Eval dataset card to be filled once the eval set exists | DATASET_CARD | Abhishek |
| Q-49 | Jhashank's repository invitation is pending. Until accepted, Hardik covers Area 3 and Area 3 issues are assigned to Hardik. Reassign when accepted. | TEAM_GUIDE, PHASES | Hardik |
| Q-50 | Fine-tuning gate values: required F1 margin over the base model, and the allowed regression tolerances per slice (ADR-023) | DECISIONS ADR-023, AI_SPEC section 12, EVALUATION section 7 | Abhishek |
| Q-51 | Location and runner for end-to-end tests (proposed: `packaging/tests/`, Area 1) | PHASES, ARCHITECTURE | Samanway |
| Q-52 | Anchoring design: Polygon contract, client library, relayer or wallet, Amoy settings (extends Q-26) | PHASES Phase 5, ADR-014 | Hardik |
| Q-53 | Speech interface shape (`transcribe(audio) -> Transcript`) agreed between Area 1 and Area 2; contract for Transcript | PHASES Phase 0, ARCHITECTURE | Abhishek |
| Q-54 | Handles `@NYN-05` in CODEOWNERS is not yet a collaborator, so GitHub may flag the line until the invite is accepted | CODEOWNERS | Hardik |
| Q-55 | INTEGRITY_SPEC section 2 says text is NFC-normalised (and line endings made `\n`) "before hashing", and section 4 says records are serialised with RFC 8785 JCS, which does not normalise Unicode. Where does NFC apply: to every string value when a record object is built (before JCS), only to named text fields (message text, transcript text, reply text), or inside canonicalisation? Does it apply to keys? This changes the Hindi test vectors. Proposal: a separate `normalize_text` step in the record builders; `canonicalize` stays pure RFC 8785; all string values are normalised | INTEGRITY_SPEC sections 2 and 4 | Hardik (covering Jhashank) |
| Q-56 | Numbers in canonical JSON: JCS formats numbers as ECMAScript doubles, so integers above 2^53 cannot be represented exactly (the Python library rfc8785 raises an error for them). The spec only says money is a string. Should such integers be rejected, and which fields may be numbers at all (seq, version, order, durations)? Proposal: reject integers outside the safe range, floats allowed only where the contract needs them (durations, confidence), everything else an integer or a string | INTEGRITY_SPEC section 4 | Hardik (covering Jhashank) |
| Q-57 | The worked example in section 6 uses a four-field message payload (`id`, `sender`, `text`, `ts`), the table in section 4 lists six fields (`id`, `sender`, `ts`, `text`, `attachment`, `source`), and the draft contracts have other names (`sender_id`, `origin`, `attachment_hash`, `deal_id`, `seq`). Which is the canonical Message object? Proposal: primitives and their test vectors are payload-agnostic (any JSON); section 6 is labelled a simplified example; the real record shapes are fixed after the contracts are agreed (PR #40) | INTEGRITY_SPEC sections 4 and 6, PR #40 | Hardik (covering Jhashank) |
| Q-58 | Which record types use the salted leaf form `H(type_byte || salt || H(payload))` and which the plain form `H(prefix || JCS(object))`? Section 5 names message, audio and transcript leaves; section 7 calls `0x22` a leaf; FR-HSK-003 says the `0x13` seal is salted; `0x14` is not described; `0x20`, `0x21`, `0x40` are used without salt. Proposal: salted leaves for `0x10`, `0x11`, `0x12`, `0x13`, `0x14`, `0x22`; plain domain hashes for `0x20`, `0x21`, `0x40`, `0x30`, `0x50` | INTEGRITY_SPEC sections 3, 5, 7 | Hardik (covering Jhashank) |
| Q-59 | Are hash operands always raw 32-byte values (as `32 zero bytes` in section 8 implies) and never the 64-character hex text, in `H(0x50 || recap_hash)`, version links and Merkle nodes? Proposal: raw bytes everywhere, hex only for storage and display | INTEGRITY_SPEC sections 2, 7, 8 | Hardik (covering Jhashank) |
| Q-60 | Edge cases of the Merkle rule that follow from "carry the odd node up": a one-leaf tree has the leaf hash as its root and an empty proof; a proof has no element for a level where the node was carried up. Proposal: confirm and state it in section 6 | INTEGRITY_SPEC section 6 | Hardik (covering Jhashank) |

## 3. Resolved

| ID | Resolution | Date | Document changed |
|---|---|---|---|
| C-01 | Confirmation = echo code (ADR-011). Idea document marked superseded. | 2026-10-25 | PRD, UX_FLOWS, DEMO_SCRIPT, source idea note |
| C-02 | Kannada = P1, after native-speaker review. | 2026-10-25 | PRD, UX_FLOWS, DEMO_SCRIPT, source idea note |
| C-03 | Speech-to-text = MVP. | 2026-10-25 | PRD, UX_FLOWS, DEMO_SCRIPT, source idea note |
| C-04 | faster-whisper (ADR-009). | 2026-10-25 | PRD, UX_FLOWS, DEMO_SCRIPT, source idea note |
| C-11 | FR-SCO-001 formula kept. Demo numbers come from the real formula; wireframe values are illustrative only. | 2026-10-25 | PRD, UX_FLOWS, DEMO_SCRIPT, source idea note |
| Q-25 | Blind Handshake: reply mode is primary; handover mode is the demo mode; first party's answers must be sealed before the second can submit (FR-HSK-007). | 2026-10-25 | PRD, UX_FLOWS, DECISIONS, DATA_MODEL, INTEGRITY_SPEC, AI_SPEC, DEMO_SCRIPT |
| Q-29 | Named dependency owner: Jhashank (Area 3). | 2026-10-25 | TEAM_GUIDE, ONBOARDING, CODEOWNERS, CLAUDE.md, AGENTS.md |
| Q-30 | Members: Samanway @notorious1337 (Area 1), Abhishek @absksync (Area 2), Jhashank @NYN-05 (Area 3), Hardik @HARDIKSINGH150206 (Area 4). | 2026-10-25 | TEAM_GUIDE, ONBOARDING, CODEOWNERS, CLAUDE.md, AGENTS.md |
| Q-31 | Document owners set in TEAM_GUIDE; Hardik is editor of shared docs. | 2026-10-25 | TEAM_GUIDE, ONBOARDING, CODEOWNERS, CLAUDE.md, AGENTS.md |
| Q-32 | Branch protection set on main and dev (see GIT_WORKFLOW section 7 for the next steps). | 2026-10-25 | TEAM_GUIDE, ONBOARDING, CODEOWNERS, CLAUDE.md, AGENTS.md |
| Q-33 | CI workflow added: `.github/workflows/ci.yml`, required checks `checks` and `secrets` on dev and main. | 2026-10-25 | GIT_WORKFLOW, DEVELOPMENT_METHODOLOGY, PHASES |
