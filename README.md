# VeriDoc

VeriDoc turns a WhatsApp deal conversation into a verified record while the conversation is still going on. It runs on the user's own laptop, finds the key terms, flags what is missing or unclear, suggests the next friendly message, builds a plain-language recap the other side confirms with a short code, and keeps a tamper-evident record that anyone can check offline.

Tagline: "From chat to verified document, while you're still chatting."

Last updated: 2026-10-25
Status: Draft v1 (documentation only; no application code yet)

VeriDoc is a drafting and record-keeping aid, not legal advice.

## Problem statement fit: LS-06

LS-06, From Handshake to Contract (Informal Agreements), Legal Services track. Core flow: **Handshake, Recap, Receipt**.

| Ask | LS-06 requirement | VeriDoc feature |
|---|---|---|
| A | Extract key terms from conversations | Term extractor, playbooks, play the moment |
| B | Flag anything ambiguous or missing | Flags, Evidence Strength score, chat recommendation |
| C | Generate a simple plain-language agreement for both sides to confirm | Recap with echo-code confirmation, Blind Handshake |
| D | Preserve the evidence trail in a tamper-evident way | Hash-based evidence vault, verify page |
| E | Do this without making the relationship feel legalistic | Friendly suggested messages; nothing for the other side to install |
| F | Produce a clear, defensible record | Verify page, dispute pack, honest limits |

Judges' six requested features: Chat and voice note import · Term extractor · Ambiguity and missing-term flags · Chat recommendation · Plain-language agreement · Hash-based evidence vault.

## Features by tier

**MVP (must work live in the demo)**
1. Chat and voice note import (WhatsApp export with media, Android and iPhone; samples; simulator)
2. Term extractor with source links
3. Ambiguity, missing-term and contradiction flags, including text versus voice
4. Chat recommendation in three tones
5. Evidence Strength score, 0 to 100
6. Blind Handshake (lite)
7. Plain-language recap in English and Hindi with echo-code confirmation
8. Hash-based evidence vault: salted Merkle tree, version chain, diff
9. Offline verify page and tamper test
10. Dispute pack (basic) with a draft Section 63 BSA certificate
11. AI safety: grounding, prompt-injection defence, human confirmation
12. Measured accuracy and trust report
13. Playbooks (supply or order; freelance or service)
14. Play the moment

**P1 (after MVP):** selective disclosure, privacy mask, share link, Kannada recap, read-aloud recap, Paper Seal, optional public anchoring, integrity red flags, stamp-duty hint, reminders, wider voice-to-text contradiction detection.

**Roadmap (not built):** Android app, installable phone web app, in-person voice sealing, UPI screenshot check, CA countersign, cloud sync, teams and billing, WhatsApp extension.

**Cut:** counterparty reliability scores, fake-chat detection claims, verdict prediction, contract template library, full payment ledger, late-interest calculator, formal-notice escalation, LoRA fine-tuning claims, RAG.

## Honest limits

Not legal advice · no verdict prediction · tamper evidence is not authenticity of the original export · does not replace documents the law requires · small models are weaker on Hinglish and Kannada · the device clock can be wrong until anchored · the echo code relies on the authenticity of the chat export · data protection duties for the counterparty's data need a lawyer's review before public launch. Details: [docs/LIMITS.md](docs/LIMITS.md). Any statement about Indian law needs a lawyer's confirmation.

All performance and accuracy figures in this repository are targets until a trust report shows measured results.

## Quick start

The code does not exist yet. When it does, follow [docs/SETUP.md](docs/SETUP.md). Commands are marked `TBD` there until then.

## Documentation index

| Document | Contents |
|---|---|
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Architecture decision records |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and diagrams |
| [docs/INTEGRITY_SPEC.md](docs/INTEGRITY_SPEC.md) | Hashing, Merkle, version chain, echo code, verification |
| [docs/AI_SPEC.md](docs/AI_SPEC.md) | Extraction pipeline, grounding, injection defence, model tiers |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Entities, retention, encryption |
| [docs/PLAYBOOKS.md](docs/PLAYBOOKS.md) | Playbook format and the two MVP playbooks |
| [docs/UX_FLOWS.md](docs/UX_FLOWS.md) | Screens S1 to S12 |
| [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) | Threats and mitigations |
| [docs/PRIVACY.md](docs/PRIVACY.md) | Data handling and DPDP notes |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Eval set, metrics, trust report |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Hardware tiers and benchmarks |
| [docs/LIMITS.md](docs/LIMITS.md) | Honest limits and exact wording |
| [docs/ROADMAP.md](docs/ROADMAP.md) | MVP, P1, roadmap, drop order |
| [docs/SETUP.md](docs/SETUP.md) | Developer setup |
| [docs/TEAM_GUIDE.md](docs/TEAM_GUIDE.md) | Team workflow and ownership |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Four-minute demo |
| [docs/JUDGE_QA.md](docs/JUDGE_QA.md) | Likely judge questions |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Definitions |
| [docs/PRIOR_WORK.md](docs/PRIOR_WORK.md) | What came from DigiVault |
| [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | Open items and source conflicts |
| [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) | Contributor and security rules |
| [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md) | Instructions for AI coding tools |

Source documents: `docs/source/VeriDoc-Final-Idea.md` and `docs/source/veridoc-wireframes.html` (the idea document and wireframes may still say "Vachan", the old working name).

## Prior work

VeriDoc is built from scratch. The design of its integrity layer is informed by the team's earlier project DigiVault; no DigiVault code is reused. See [docs/PRIOR_WORK.md](docs/PRIOR_WORK.md).

## Licence

TBD.
