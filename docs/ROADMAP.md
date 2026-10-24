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

Selective disclosure · privacy mask on exports · share link · Kannada recap (after native-speaker review) · read-aloud recap · Paper Seal · optional public anchoring · integrity red flags · stamp-duty hint for one or two states · reminders for agreed dates · wider voice-to-text contradiction detection.

### Roadmap (not built)

Android app with "Share to VeriDoc" · installable phone web app · in-person voice sealing (Handshake Mode) · UPI screenshot check · CA countersign · cloud sync · teams and billing · WhatsApp extension.

## 2. Cut list (will not be built)

Counterparty reliability scores · fake-chat detection claims · verdict prediction · contract template library · full payment ledger · late-interest calculator · formal-notice escalation · LoRA fine-tuning claims · RAG. Reasons are in [DECISIONS](DECISIONS.md) ADR-020.

## 3. Drop order if time runs short

1. Share link
2. Blind Handshake
3. Kannada
4. Pendrive tiers

**Never drop:** import, term extractor, flags, chat recommendation, recap, vault, verify page.

P1 work does not begin until the MVP acceptance criteria pass.

## 4. Suggested build order

The team agrees contracts first (TEAM_GUIDE). Then four areas work in parallel against mock data.

| Phase | Area 1 | Area 2 | Area 3 | Area 4 |
|---|---|---|---|---|
| 0. Contracts | Agree schemas together | | | |
| 1. Skeleton | WhatsApp parser, samples | Rules parsers, playbook loader | Hashing, JCS, test vectors | Screens on mock data, launcher |
| 2. Core | Media, voice transcription | Extraction, flags, score, suggestion | Merkle, chain, vault, verify page | Live workspace via SSE |
| 3. Trust | Preview and error states | AI refinement, grounding, injection tests, eval set | Echo code, tamper tests, dispute pack | Recap, receipt, verify screens |
| 4. Polish | Voice play-the-moment | Hindi templates, trust report | Encryption, recovery | Packaging, tiers, antivirus test |
| 5. Demo | All | Trust report | All | Recorded backup |

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
