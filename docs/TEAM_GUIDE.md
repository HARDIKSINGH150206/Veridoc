# Team Guide

This guide tells the four team members how to work together: branching, commits, reviews, the definition of done, priority tags, ownership areas and the merge-conflict rules. Member names are `TBD`; roles are described only.

Last updated: 2026-10-25
Status: Draft v1

## 1. Ownership areas

| Area | Owns | Role | Member |
|---|---|---|---|
| 1. Ingest, Voice and Agreement | `packages/ingest`, `apps/api/routers/ingest.py`, `apps/api/routers/agreement.py`, `playbooks/templates/`, sample chats | Ingest and agreement lead | TBD |
| 2. Intelligence | `packages/intelligence`, `playbooks/` (except `playbooks/templates/`), `eval/`, `apps/api/routers/analysis.py` | AI and rules lead | TBD |
| 3. Integrity and Vault | `packages/integrity`, `packages/vault`, `apps/verify`, `test-vectors/`, `apps/api/routers/vault.py`, `apps/api/routers/export.py` | Integrity lead | TBD |
| 4. Frontend and Packaging | `apps/web`, `packaging/`, `apps/api/main.py` | UI and release lead | TBD |

Shared by all, changed only by small reviewed pull requests: `packages/contracts`, `docs/`, `.github/`.

Dependency files (`pyproject.toml`, `uv.lock`) have one named owner: TBD.

Hotspots and their owners: contracts process (all four, by pull request), dependency files (named owner TBD), design tokens `apps/web/assets/design-tokens.css` (Area 4), migrations `packages/vault/migrations/` (Area 3), `apps/api/main.py` (Area 4, rarely edited because of router auto-discovery).

The release lead (Area 4) combines changelog fragments into `CHANGELOG.md` at phase end. `models/manifest.json` and `scripts/` are changed by the area that needs the change, with a review from the Area 2 lead (models) or the Area 3 lead (scripts that touch hashing).

### Document owners

| Document | Owner area |
|---|---|
| PRD, ROADMAP, DEMO_SCRIPT, JUDGE_QA, GLOSSARY, OPEN_QUESTIONS | TBD (shared; one named editor) |
| ARCHITECTURE, DECISIONS | All areas review; one named editor TBD |
| INTEGRITY_SPEC, DATA_MODEL, THREAT_MODEL | Area 3 |
| AI_SPEC, PLAYBOOKS, EVALUATION | Area 2 |
| UX_FLOWS, SETUP, PERFORMANCE, DEMO_DAY_RUNBOOK, RELEASE_CHECKLIST | Area 4 |
| ONBOARDING, GIT_WORKFLOW, PHASES, DEVELOPMENT_METHODOLOGY | TBD (shared; one named editor) |
| USER_RESEARCH, DATASET_CARD, MODEL_CARD | Area 2 (USER_RESEARCH: TBD) |
| PRIVACY, LIMITS | Area 3 with Area 4 for UI copy |
| PRIOR_WORK | TBD |

## 2. Merge-conflict rules

1. **Contracts first.** On day 1 the team agrees `packages/contracts` together: Message, VoiceNote, Term, Flag, Score, Suggestion, HandshakeAnswer, Recap, Confirmation, Version, Receipt, DisputePack. Any later change is its own small pull request reviewed by all four.
2. **One owner per hotspot.** `apps/api/main.py` (Area 4), `apps/web/components/` (Area 4), dependency files (named owner). Others request changes instead of editing.
3. **Short branches.** One feature per branch, merged within 1 to 2 days. Unfinished work merges early behind a feature flag.
4. **Rebase every morning.** `git pull --rebase origin dev` before starting work, and pull before you push.
5. **Never commit generated files:** reports, caches, model weights, `node_modules`, build output.
6. **One file per item.** One chat per eval file, one screen per folder, one playbook per YAML file.
7. **Formatter and linter run on commit** (ruff via pre-commit), so formatting never causes conflicts.
8. **The frontend builds against mock data** that matches the contracts, so UI work never waits on the backend.
9. **AI coding tools** (Claude Code, Codex) are run by each member only inside that member's area.
10. **Router auto-discovery.** `apps/api/main.py` loads every module in `apps/api/routers/` (ADR-022). Nobody edits `main.py` to add a route.
11. **Changelog fragments.** Each pull request adds `changes/<branch-name>.md` and never edits `CHANGELOG.md`. The release lead combines fragments at phase end.
12. **Migrations are Area 3 only.** Other areas request schema changes. Alembic multiple heads are fixed by Area 3 (see ONBOARDING section 22).
13. **One dependency pull request per day.** The dependency owner batches changes so `uv.lock` never conflicts.
14. **Design tokens in one file** (`apps/web/assets/design-tokens.css`, Area 4). Every screen has its own CSS file.
15. **Line endings and style files.** `.gitattributes` (LF) and `.editorconfig` are in the repo; do not override them locally.
16. **No generated files in Git:** reports, OpenAPI dumps, build output, caches.

Onboarding for new members: [ONBOARDING](ONBOARDING.md). Phase plan: [PHASES](PHASES.md). Working method: [DEVELOPMENT_METHODOLOGY](DEVELOPMENT_METHODOLOGY.md).

## 3. Branching

Full detail is in [GIT_WORKFLOW](GIT_WORKFLOW.md). In short: `main` is stable and receives phase releases only; `dev` is integration; every feature branch starts from `dev` and merges back into `dev` by pull request.

| Pattern | Use |
|---|---|
| `feat/<area>-<name>` | A feature, for example `feat/ingest-android-parser` |
| `fix/<name>` | A bug fix |
| `docs/<name>` | Documentation |
| `chore/<name>` | Tooling, dependencies, configuration |
| `hotfix/<name>` | An urgent fix, branched from `main` |

`main` and `dev` are protected on GitHub: pull request required, force pushes and deletion blocked.

## 4. Commits

Conventional Commits, small and logical.

| Type | Use |
|---|---|
| `feat` | New behaviour |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Tests only |
| `refactor` | No behaviour change |
| `chore` | Tooling, dependencies |
| `perf` | Performance |

Format: `type(scope): short summary`, for example `feat(ingest): parse iPhone export headers`. Body explains why, if not obvious.

## 5. Pull requests and reviews

1. Use the pull request template: summary, area, linked requirement IDs, checklist, whether contracts changed.
2. Keep pull requests small (aim for under about 300 changed lines). Add a changelog fragment in `changes/` (see `changes/README.md`).
3. One reviewer from another area. Contracts, hashing and verify changes need the Area 3 lead. Contract changes need all four.
4. Reviewers check: requirement IDs, tests, wording rules, no content in logs, ownership boundaries.
5. Squash or rebase merge; keep history readable.
6. Anyone who is stuck for more than an hour asks in the team channel.

## 6. Definition of done

A change is done when:

1. Tests exist and pass, inside the package they test.
2. ruff passes and mypy passes.
3. It works with the network off (offline check).
4. Docs are updated (PRD acceptance criteria, specs, UX flows as relevant).
5. If a new input or boundary was added, the THREAT_MODEL row is added or updated.
6. Hashing, Merkle, version chain, echo code or verify changes also update INTEGRITY_SPEC and the test vectors, and all tamper tests pass.
7. No secrets, real chats, model weights or content in logs.
8. Wording follows LIMITS (tamper-evident, court-ready evidence package, targets are targets).
9. The change is linked to requirement IDs.

## 7. Priority tags

| Tag | Meaning |
|---|---|
| MVP | Must work live in the demo |
| P1 | After MVP acceptance passes |
| Roadmap | Not built |

Issues and pull requests carry one tag. Follow the drop order if time runs short: share link, Blind Handshake, Kannada, pendrive tiers. Never drop import, term extractor, flags, chat recommendation, recap, vault, verify page.

## 8. Working with AI coding tools

1. Each member runs Claude Code or Codex only inside their own area.
2. The tool reads `CLAUDE.md` or `AGENTS.md`. If a change is needed outside the area, the tool describes it and a human routes it to the owner.
3. Tools never push and never open pull requests. A human pushes.
4. Humans review all generated code before merge.

## 9. Day-1 checklist

1. Agree `packages/contracts` together (rule 1).
2. Name the dependency owner and fill CODEOWNERS.
3. Name document owners.
4. Set up pre-commit with ruff and gitleaks.
5. Add CI workflows.
6. Fill OPEN_QUESTIONS owners.
