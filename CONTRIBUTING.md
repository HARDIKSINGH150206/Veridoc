# Contributing

Short rules for contributors. The full workflow is in [docs/TEAM_GUIDE.md](docs/TEAM_GUIDE.md).

Last updated: 2026-10-25
Status: Draft v1

1. Work only in your ownership area. Changes to `packages/contracts`, `docs/` and `.github/` go through a small reviewed pull request.
2. Branch names: `feat/<area>-<name>`, `fix/<name>`, `docs/<name>`. One feature per branch, merged within 1 to 2 days.
3. Branch from `dev` and run `git pull --rebase origin dev` before you start each day. Pull requests go into `dev`; `main` gets phase releases only. New here? Start with [docs/ONBOARDING.md](docs/ONBOARDING.md).
4. Use Conventional Commits and small commits. Add a changelog fragment in `changes/` to every pull request.
5. Link every pull request to requirement IDs from the PRD.
6. Meet the definition of done in TEAM_GUIDE: tests, ruff, mypy, offline check, docs updated, threat model row updated for new inputs.
7. Never commit secrets, `.env` files, model weights, real chats or generated reports.
8. Never log message content, transcripts or identifiers.
9. Use the wording in [docs/LIMITS.md](docs/LIMITS.md): tamper-evident, court-ready evidence package, targets are targets.
10. If unsure, stop, ask, and add the question to `docs/OPEN_QUESTIONS.md`.
