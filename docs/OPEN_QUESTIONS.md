# Open Questions

Every `TBD` in the repository, and every conflict found between the source documents, is recorded here. Owners are `TBD` until the team assigns them. When a question is answered, move it to the "Resolved" table with the date and the document changed.

Last updated: 2026-10-25
Status: Draft v1

## 1. Conflicts between sources

The ground rule is: this prompt wins, then `docs/source/VeriDoc-Final-Idea.md`, then `docs/source/veridoc-wireframes.html`. These conflicts were found while writing the first draft.

| ID | Conflict | Sources | Resolution used | Owner |
|---|---|---|---|---|
| C-01 | Counterparty confirmation: the idea document uses a one-tap link; the wireframes (S6, S12) and the master prompt use an echo code replied in WhatsApp | Idea section 2 and 4; wireframes S6, S12 | Echo code (ADR-011) | TBD |
| C-02 | Kannada recap is listed in the idea document's core flow and screen 2; the master prompt and wireframe S6 make it P1 | Idea sections 2, 4; wireframe S6 | P1 after native-speaker review | TBD |
| C-03 | Speech to text: the idea document calls voice-note support a strong add-on; wireframe S11 shows "Speech to text: Not enabled, Roadmap"; the master prompt makes it MVP with faster-whisper | Idea section 4; wireframe S11 | MVP, faster-whisper (ADR-009) | TBD |
| C-04 | Speech engine: idea names Whisper.cpp; master prompt names faster-whisper | Idea section 7 | faster-whisper | TBD |
| C-05 | Model: idea names Qwen2.5 7B Q4 with 3B fallback; master prompt says model choices are TBD with hardware tiers (7B, 3B, 1.5B, safe mode) | Idea section 7 | Tiers, models TBD pending benchmarks | TBD |
| C-06 | Backend: idea says "Python FastAPI or Node"; master prompt fixes Python | Idea section 7 | Python, FastAPI | TBD |
| C-07 | Frontend: idea says static HTML, JS and Tailwind; master prompt requires bundled assets with no CDN | Idea section 7 | Bundled CSS and JS, no CDN; whether Tailwind is used as a build-time tool is Area 4's choice | TBD |
| C-08 | Prior work: idea says the integrity layer is "reused from our earlier DigiVault design"; master prompt says build from scratch with no code reuse | Idea section 7 | From scratch; design ideas only (PRIOR_WORK) | TBD |
| C-09 | Anchoring: the idea document lists blockchain anchoring as roadmap; master prompt makes optional anchoring P1 | Idea section 4; wireframe S8 (P1) | P1 | TBD |
| C-10 | Deal types: wireframe S2 shows only supply or order enabled and "Freelance job, later"; master prompt ships two playbooks in the MVP | Wireframe S2 | Two playbooks in the MVP | TBD |
| C-11 | Evidence Strength example: wireframes show 68 with "Present 5 of 8, Clear 3 of 8, Acknowledged 2 of 8" and the idea demo shows 68 then 90; the formula in PRD FR-SCO-001 gives 61 for the same chat | Wireframe S3; idea section 11 | Formula wins; wireframe numbers are placeholders. Demo numbers must come from the real formula | TBD |
| C-12 | Dispute-readiness view ("here is what you could prove today") appears as an add-on in the idea document and is not in the master prompt's feature list | Idea section 4 | Not built; Evidence Strength score covers the need | TBD |
| C-13 | Idea document says a pendrive of 16 GB; master prompt says USB 3 stick, exFAT, without a size | Idea sections 3, 6 | USB 3, exFAT; size TBD | TBD |
| C-14 | Wireframe S12 and S6 mention the word "fingerprint" for the hash; master prompt uses "hash" | Wireframe S6 | UI may use "fingerprint" as plain-language copy; docs use "hash" | TBD |
| C-15 | The idea document calls the stick "encrypted vault ... Eject" in its header wireframe; the PRD does not specify an Eject control | Idea section 5 | Optional UI control; Area 4 decides | TBD |

## 2. Open items

### Product and legal

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-01 | Product owner, engineering owners and legal reviewer names | PRD section 1 | TBD |
| Q-02 | Lawyer review of every statement about Indian law, including whether and how chat agreements may be valid contracts | PRD section 13, JUDGE_QA | TBD |
| Q-03 | Which deal types need a written, stamped or registered document, and the exact legal-hint wording | PLAYBOOKS | TBD |
| Q-04 | Form and applicability of the draft Section 63 BSA certificate for chat evidence | PRD FR-DSP-003 | TBD |
| Q-05 | DPDP: lawful basis, notice and consent for the counterparty's data; counterparty deletion requests; breach process | PRIVACY section 8 | TBD |
| Q-06 | Legal retention period for deal records | DATA_MODEL section 6, PRD section 11 | TBD |
| Q-07 | Stamp-duty hints: which one or two states, and verified figures (P1) | PRD FR-STP-001 | TBD |
| Q-08 | Licence of the repository | README | TBD |
| Q-09 | Whether DigiVault's repository is public | PRIOR_WORK | TBD |
| Q-10 | Hackathon event name, date, venue and any rules that affect scope | DEMO_SCRIPT, ROADMAP | TBD |
| Q-11 | Calendar dates for build phases | ROADMAP | TBD |
| Q-12 | Revenue model hypotheses to validate | ROADMAP section 5 | TBD |

### AI, language and evaluation

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-13 | Exact extraction models per tier (about 7B, 3B, 1.5B), chosen by benchmark | AI_SPEC, PERFORMANCE, DECISIONS ADR-008, manifest | TBD |
| Q-14 | Speech models (small, base) and versions | AI_SPEC, manifest | TBD |
| Q-15 | Voice-segment confidence threshold for "needs review" | AI_SPEC section 7, PRD FR-VOI-003 | TBD |
| Q-16 | Per-language accuracy targets (Hinglish, Kannada-English) after the first trust report | EVALUATION section 4 | TBD |
| Q-17 | Native-speaker review of Hindi templates and limits wording | PLAYBOOKS, LIMITS | TBD |
| Q-18 | Native-speaker review of Kannada templates (P1) | PRD FR-KAN-001 | TBD |
| Q-19 | Eval set labellers and the reviewer roster | EVALUATION section 2 | TBD |
| Q-20 | Trust report command name and location | EVALUATION section 6, SETUP | TBD |

### Integrity and security

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-21 | Final domain-separation byte values and field lists, fixed by test vectors | INTEGRITY_SPEC | TBD |
| Q-22 | Echo-code length (4 characters, 20 bits) is enough, or should it be longer | INTEGRITY_SPEC section 7 | TBD |
| Q-23 | Argon2id parameters tuned for 8 GB laptops | DATA_MODEL section 5 | TBD |
| Q-24 | Maximum import size and archive limits | PRD FR-IMP-002, ARCHITECTURE section 12 | TBD |
| Q-25 | Blind Handshake: is handover mode acceptable as "blind" in the lite version, and what wording describes reply mode | PRD FR-HSK-001, UX_FLOWS S5 | TBD |
| Q-26 | Anchoring: relayer or wallet approach and cost for Polygon Amoy (P1) | DECISIONS ADR-014 | TBD |
| Q-27 | Signed releases and publication of the verify page hash | THREAT_MODEL T19 | TBD |
| Q-28 | Security contact address and response timelines | SECURITY | TBD |

### Engineering and packaging

| ID | Question | Where it appears | Owner |
|---|---|---|---|
| Q-29 | Named dependency owner for `pyproject.toml` and `uv.lock` (CODEOWNERS currently uses @TBD-member-4 as a placeholder) | TEAM_GUIDE, CODEOWNERS | TBD |
| Q-30 | Member names for Areas 1 to 4 | TEAM_GUIDE, CODEOWNERS | TBD |
| Q-31 | Document owners for PRD, ARCHITECTURE, DECISIONS, PRIOR_WORK | TEAM_GUIDE | TBD |
| Q-32 | GitHub branch protection settings for `main` | TEAM_GUIDE | TBD |
| Q-33 | CI workflows (tests, lint, gitleaks, pip-audit, offline check) | SETUP, `.github/workflows/` | TBD |
| Q-34 | PDF renderer: fpdf2 with uharfbuzz, or browser rendering | ARCHITECTURE section 8 | TBD |
| Q-35 | Tier detection rule for "old CPU" | PERFORMANCE section 1 | TBD |
| Q-36 | The three benchmark laptops | PERFORMANCE section 4 | TBD |
| Q-37 | All install, run, test, lint, type-check, trust-report and pendrive-build commands | SETUP, CLAUDE.md, AGENTS.md | TBD |
| Q-38 | Whether Tailwind is used as a build-time tool (output must still be bundled with no CDN) | Conflict C-07 | TBD |
| Q-39 | Demo roles: presenter, second person, operator | DEMO_SCRIPT | TBD |
| Q-40 | Confirmation-rate, time-to-confirm and score-improvement baselines from a pilot | PRD section 15 | TBD |
| Q-41 | Generate real test vectors with a script; Python and JS must both reproduce them. | INTEGRITY_SPEC sections 6 and 13 | TBD |

## 3. Resolved

| ID | Resolution | Date | Document changed |
|---|---|---|---|
| (none yet) | | | |
