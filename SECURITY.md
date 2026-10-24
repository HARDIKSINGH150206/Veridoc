# Security Policy

How to report a vulnerability, and the rules for secrets and keys in this repository.

Last updated: 2026-10-25
Status: Draft v1

## Reporting a vulnerability

1. Do not open a public issue for a security problem.
2. Contact the maintainers privately: contact address `TBD` (see OPEN_QUESTIONS).
3. Include: what you found, steps to reproduce, the affected file or feature, and the impact. Do not include real user chats.
4. We aim to acknowledge a report within a few days and to agree a fix and disclosure plan with you. Exact timelines are `TBD`.

## Scope

In scope: the vault and encryption, the integrity engine and verify page, the local API, import parsers, the packaging scripts. See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Secrets

1. No secrets, keys, tokens, passphrases or real chats in the repository, in issues or in pull requests.
2. `.env` files are git-ignored. Only `.env.example` with names (no values) is committed.
3. Model weights are never committed; `models/manifest.json` holds names and SHA-256 hashes only.
4. gitleaks runs in pre-commit and CI. If a secret is committed by mistake, tell the maintainers, rotate it, and remove it from history.

## Key handling

1. The vault passphrase is never stored. It derives a key with Argon2id.
2. The recovery key is shown once at setup and must be kept by the user; it is never logged or stored in plain form.
3. Keys never appear in logs, error messages or exports.
4. Anchoring (P1) sends only hashes. The share link (P1) keeps its key in the URL fragment and never sends it to a server.
5. Dependencies are audited with pip-audit; the lockfile is reviewed by the dependency owner.
