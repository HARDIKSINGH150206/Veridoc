# Roadmap

This document sets out what is MVP, P1 and roadmap, what is cut, what is dropped first if time runs short, and the path to a SaaS product. Nothing in the roadmap tier is built or promised.

Last updated: 2026-10-25
Status: Draft v1

## 1. Tiers

### MVP (must work live in the demo)

| # | Feature |
|---|---|
| 1 | Chat and voice note import |
| 2 | Term extractor |
| 3 | Ambiguity, missing-term and contradiction flags (text and voice) |
| 4 | Chat recommendation |
| 5 | Evidence Strength score |
| 6 | Blind Handshake (lite) |
| 7 | Plain-language recap (English, Hindi) with echo-code confirmation |
| 8 | Hash-based evidence vault with versions and diff |
| 9 | Verify page with tamper test |
| 10 | Dispute pack (basic) |
| 11 | AI safety |
| 12 | Measured accuracy and trust report |
| 13 | Playbooks (two) |
| 14 | Play the moment |

### P1 (after MVP acceptance passes)

Selective disclosure · privacy mask on exports · share link · Kannada recap (after native-speaker review) · read-aloud recap · Paper Seal · optional public anchoring · integrity red flags · stamp-duty hint for one or two states · reminders for agreed dates · wider voice-to-text contradiction detection · optional fine-tuning with an eval gate (ADR-023).

### Roadmap (not built)

Android app with "Share to VeriDoc" · installable phone web app · in-person voice sealing (Handshake Mode) · UPI screenshot check · CA countersign · cloud sync · teams and billing · WhatsApp extension.

## 2. Cut list (will not be built)

Counterparty reliability scores · fake-chat detection claims · verdict prediction · contract template library · full payment ledger · late-interest calculator · formal-notice escalation · fine-tuning claims without an eval gate (ADR-023) · RAG. Reasons are in [DECISIONS](DECISIONS.md) ADR-020.

## 3. Drop order if time runs short

1. Share link
2. Blind Handshake
3. Kannada
4. Pendrive tiers

**Never drop:** import, term extractor, flags, chat recommendation, recap, vault, verify page.

P1 work does not begin until the MVP acceptance criteria pass.

## 4. Suggested build order

The phase plan with per-area tasks and gates is in [PHASES](PHASES.md). The summary below is kept consistent with it: Phase 0 Setup, Phase 1 Foundation, Phase 2 Core loop, Phase 3 Agreement, Phase 4 Proof and polish, Phase 5 P1 if time allows.

| Phase | Theme | Main outcome |
|---|---|---|
| 0 Setup | Environment, CI, contracts, walking skeleton | A stub path runs through all four areas |
| 1 Foundation | Parser, rules, hashing, first screens | Real import, rules terms, Merkle root, S1 to S3 on fixtures |
| 2 Core loop | Voice, AI, flags, score, suggestion, vault write | Import to flags to suggestion works end to end |
| 3 Agreement | Recap, echo code, Blind Handshake, versions | A recap is confirmed and a version chain exists |
| 4 Proof and polish | Verify page, tamper tests, dispute pack, packaging, benchmarks | Demo-ready on a second laptop |
| 5 P1 if time allows | Selective disclosure, mask, share link and others | Only after MVP acceptance passes |

Calendar dates are `TBD` (see OPEN_QUESTIONS).

## 5. Path to SaaS

| Stage | Offer | Needs |
|---|---|---|
| 1. Free offline individual | The MVP and P1 on a laptop or stick | Pilot users; lawyer review of wording; DPDP review |
| 2. Phone | Installable web app, then Android app with Share to VeriDoc | Port of the engine to run on a phone; smaller models |
| 3. Paid team tier | Encrypted sync, shared deals, billing, audit export for firms | Accounts, a cloud service, security review |
| 4. Professional layer | CA countersign; lawyer or CA review marketplace | Partners; professional liability review |
| 5. Integrations | WhatsApp extension; UPI screenshot check; anchoring service | Platform policies; partner APIs |

Revenue ideas are hypotheses (`TBD`): a paid team plan, per-pack fees, a professional marketplace. None is validated.

## 6. Exit criteria for each tier

| Tier | Done when |
|---|---|
| MVP | All MVP acceptance criteria in the PRD pass; trust report exists; tamper tests pass; demo runs offline on a second laptop |
| P1 | Each P1 requirement passes its acceptance criteria; threat model rows updated |
| Roadmap | Starts only with a new PRD |
