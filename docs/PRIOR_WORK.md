# Prior Work

This document records what VeriDoc's design takes from the team's earlier project, DigiVault, and confirms that all VeriDoc code is new.

Last updated: 2026-10-25
Status: Draft v1

## Statement

VeriDoc is being built from scratch. The design of its integrity layer is informed by the team's earlier project DigiVault. No DigiVault code, files, data or dependencies are reused.

## Design ideas that came from DigiVault

| Idea | How it appears in VeriDoc |
|---|---|
| Hash every record | Per-message, per-voice-note and per-transcript hashes (INTEGRITY_SPEC) |
| Merkle commitment | A salted Merkle tree whose root is the commitment (INTEGRITY_SPEC) |
| Chain of versions | The version chain (INTEGRITY_SPEC) |
| Offline verification | A standalone verify page (ADR-015) |
| Timestamps | Device time first, optional anchoring later (ADR-014) |

New in VeriDoc and not from DigiVault: domain separation, RFC 8785 canonicalisation, cross-language test vectors, the AI layer, playbooks, Blind Handshake, echo-code confirmation, voice-note handling and the dispute pack.

## Why it is recorded

1. Honesty with judges and users about what is new.
2. A clean licence position: nothing inherited.
3. Contributors know not to copy code from DigiVault. If someone wants to reuse an idea, they write it fresh and link it to a requirement.

## Open items

- Licence of VeriDoc is `TBD` (see OPEN_QUESTIONS).
- Whether DigiVault's repository is public is `TBD`; either way, no code is copied.
