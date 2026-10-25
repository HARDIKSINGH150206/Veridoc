# Team Guide

This guide tells the four team members how to work together: branching, commits, reviews, the definition of done, priority tags, ownership areas and the merge-conflict rules. Members and their GitHub handles are listed below. Jhashank's repository invitation is still pending, so Hardik covers Area 3 work until it is accepted.

Last updated: 2026-10-25
Status: Draft v1

## 1. Ownership areas

| Area | Owns | Role | Member |
|---|---|---|---|
| 1. Ingest, Agreement and Release | `packages/ingest`, `apps/api/routers/ingest.py`, `apps/api/routers/agreement.py`, `playbooks/templates/`, `packaging/`, sample chats and demo voice notes | Ingest, agreement and release lead | Samanway (@notorious1337) |
| 2. AI and ML | `packages/intelligence`, `playbooks/` (except `playbooks/templates/`), `eval/`, `apps/api/routers/analysis.py` | AI and ML lead | Abhishek (@absksync) |
| 3. Backend, Integrity and Vault | `apps/api/main.py`, `packages/contracts` (steward), `packages/integrity` (except `packages/integrity/anchoring/`), `packages/vault`, `test-vectors/`, `apps/api/routers/vault.py`, `apps/api/routers/export.py`, `.github/workflows/`, `pyproject.toml`, `uv.lock` | Backend and integrity lead | Jhashank (@NYN-05, invitation pending; Hardik covers until accepted) |
| 4. Frontend and Blockchain | `apps/web`, `apps/verify`, `packages/integrity/anchoring/` | Frontend and blockchain lead; project release lead | Hardik (@HARDIKSINGH150206) |

Shared by all, changed only by small reviewed pull requests: `packages/contracts` (steward: Jhashank; every change still needs all four reviewers), `docs/`, `.github/` (except `.github/workflows/`, Area 3).

Dependency files (`pyproject.toml`, `uv.lock`) are owned by Area 3 (Jhashank).

**Hotspot owners:**

| Hotspot | Owner |
|---|---|
| Release lead (merge `dev` into `main`, tags, changelog) | Hardik |
| Dependency files and migrations | Jhashank |
| Design tokens `apps/web/assets/design-tokens.css` | Hardik |
| Contracts steward (`packages/contracts`) | Jhashank |
| `apps/api/main.py` (rarely edited because of router auto-discovery) | Jhashank |
| Anchoring (`packages/integrity/anchoring/`) | Hardik |
| Hardware tier thresholds and model choice | Abhishek |

While Jhashank's invitation is pending, Hardik does the Area 3 work and Area 3 issues are assigned to Hardik. When Jhashank accepts, the issues are reassigned (OPEN_QUESTIONS Q-49).

The release lead (Hardik) combines changelog fragments into `CHANGELOG.md` at phase end. `models/manifest.json` and `scripts/` are changed by the area that needs the change, with a review from Abhishek (models) or Jhashank (scripts that touch hashing).

### Document owners

| Document | Owner area |
|---|---|
| PRD, ROADMAP, JUDGE_QA, GLOSSARY, OPEN_QUESTIONS | Shared; Hardik is the named editor |
| ARCHITECTURE, DECISIONS | All areas review; Hardik is the named editor |
| INTEGRITY_SPEC, DATA_MODEL, THREAT_MODEL | Area 3 (anchoring sections: Area 4) |
| AI_SPEC, PLAYBOOKS, EVALUATION, MODEL_CARD, DATASET_CARD | Area 2 |
| UX_FLOWS | Area 4 |
| SETUP, PERFORMANCE, DEMO_SCRIPT, DEMO_DAY_RUNBOOK, USER_RESEARCH | Area 1 (tier thresholds in PERFORMANCE: Area 2) |
| RELEASE_CHECKLIST, GIT_WORKFLOW | Area 4 (Hardik, release lead) |
| ONBOARDING, PHASES, DEVELOPMENT_METHODOLOGY | Shared; Hardik is the named editor |
| PRIVACY, LIMITS | Area 3 with Area 4 for UI copy |
| PRIOR_WORK | Hardik |

## 1a. Working model (from 2026-10-25)

Every issue is either independent or integration. The label `type:integration` marks the second kind; an issue without it is independent.

| Issue type | How to recognise it | Who builds | Who merges | Reviewers |
|---|---|---|---|---|
| **Independent** | Touches only files in one area (the owner's own folders) and no seam | The area owner | The area owner, into `dev`, after CI passes | Optional: a teammate may review; not required for merge |
| **Integration** (label `type:integration`) | Touches two or more areas, `packages/contracts`, or a seam listed in DEVELOPMENT_METHODOLOGY section 11 (verify page and hashing, model tiers and launcher, AI output and workspace screen, recap and handshake with the vault, voice interface) | Hardik (area owners build their own part on a branch if useful) | Hardik, into `dev`, after CI passes | The affected area owners, who are also assignees |

Rules:
1. Work goes through a pull request into `dev`. CI (`checks` and `secrets`) must pass before anyone merges.
2. Never merge, close or push to someone else's pull request. To change it, comment on it.
3. If an independent issue turns out to need files in another area, in `packages/contracts` or at a seam, stop, say so on the issue, and Hardik relabels it `type:integration`.
4. The label `blocked` means the issue waits on another pull request or issue (named in a comment). Do not work around it.
5. Contract changes are integration issues and still need all four reviewers.
6. Phase releases (`dev` into `main`) stay with the release lead (Hardik).

## 2. Merge-conflict rules

1. **Contracts first.** On day 1 the team agrees `packages/contracts` together: Message, VoiceNote, Term, Flag, Score, Suggestion, HandshakeAnswer, Recap, Confirmation, Version, Receipt, DisputePack. Any later change is its own small pull request reviewed by all four.
2. **One owner per hotspot.** `apps/api/main.py` (Area 3), `apps/web/components/` (Area 4), dependency files and migrations (Area 3). Others request changes instead of editing.
3. **Short branches.** One feature per branch, merged within 1 to 2 days. Unfinished work merges early behind a feature flag.
4. **Rebase every morning.** `git pull --rebase origin dev` before starting work, and pull before you push.
5. **Never commit generated files:** reports, caches, model weights, `node_modules`, build output.
6. **One file per item.** One chat per eval file, one screen per folder, one playbook per YAML file.
7. **Formatter and linter run on commit** (ruff via pre-commit), so formatting never causes conflicts.
8. **The frontend builds against mock data** that matches the contracts, so UI work never waits on the backend.
9. **AI coding tools** (Claude Code, Codex) are run by each member only inside that member's area.
10. **Router auto-discovery.** `apps/api/main.py` loads every module in `apps/api/routers/` (ADR-022). Nobody edits `main.py` to add a route.
11. **Changelog fragments.** Each pull request adds `changes/<branch-name>.md` and never edits `CHANGELOG.md`. The release lead combines fragments at phase end.
12. **Migrations are Area 3 only (Jhashank).** Other areas request schema changes. Alembic multiple heads are fixed by Area 3 (see ONBOARDING section 22).
13. **One dependency pull request per day.** The dependency owner batches changes so `uv.lock` never conflicts.
14. **Design tokens in one file** (`apps/web/assets/design-tokens.css`, Area 4, Hardik). Every screen has its own CSS file.
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
3. Independent issues: the owner merges after CI passes; a review from another area is welcome but not required. Integration issues: Hardik merges, and the affected owners review. Contracts and hashing changes need Jhashank (Area 3); verify-page changes need Hardik (Area 4) and Jhashank. Contract changes need all four (see section 1a).
4. Reviewers check: requirement IDs, tests, wording rules, no content in logs, ownership boundaries.
5. Squash merge into `dev`; keep history readable.
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
10. **No hardcoding** (see CLAUDE.md): configuration only from `apps/api/settings.py`, business rules in playbooks, templates and the model manifest, stubs only in tests or demo mode with `# STUB: replaced by #<issue>`, no sample names or amounts in logic. `python scripts/check_hardcoding.py` passes.

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
2. Confirm CODEOWNERS handles (done: see `.github/CODEOWNERS`).
3. Confirm document owners (done: table above).
4. Set up pre-commit with ruff and gitleaks.
5. Add CI workflows.
6. Fill OPEN_QUESTIONS owners.
7. Jhashank accepts the repository invitation; Area 3 issues are reassigned from Hardik.
