# AGENTS.md

Instructions for OpenAI Codex in the VeriDoc repository. The same rules are in `CLAUDE.md` for Claude Code.

Last updated: 2026-10-25
Status: Draft v1

## Project summary

VeriDoc turns a WhatsApp deal conversation into a verified record while the chat is still going on. It runs locally, extracts terms with rules plus a small local model, flags ambiguity and gaps, suggests the next message, builds a template-based recap confirmed by an echo code, and keeps a tamper-evident vault with an offline verify page. Problem statement LS-06. It is a drafting and record-keeping aid, not legal advice. The project is built from scratch (see `docs/PRIOR_WORK.md`).

Read first: [ONBOARDING](docs/ONBOARDING.md), [PHASES](docs/PHASES.md), [PRD](docs/PRD.md), [ARCHITECTURE](docs/ARCHITECTURE.md), [INTEGRITY_SPEC](docs/INTEGRITY_SPEC.md), [AI_SPEC](docs/AI_SPEC.md), [DECISIONS](docs/DECISIONS.md). Also: [TEAM_GUIDE](docs/TEAM_GUIDE.md), [LIMITS](docs/LIMITS.md), [THREAT_MODEL](docs/THREAT_MODEL.md).

## Hard rules

1. Never push to a remote and never open pull requests. Create branches and commit locally only. A human pushes.
2. Never commit secrets, `.env` files, model weights or real user chats.
3. The AI layer must never write to the hash path or the vault directly. All terms pass through human confirmation.
4. Any change to hashing, Merkle, version chain, echo code or verify logic must update `docs/INTEGRITY_SPEC.md` and the cross-language test vectors in the same change, and must keep all tamper tests passing.
5. Never log message content, transcripts or identifiers.
6. Use "tamper-evident", never "tamper-proof", in code comments and UI copy. Say "court-ready evidence package" for the dispute pack.
7. Performance and accuracy numbers are targets until measured by a trust report.
8. Follow the drop order (share link, Blind Handshake, Kannada, pendrive tiers). Do not start P1 work until MVP acceptance criteria pass. Never drop import, term extractor, flags, chat recommendation, recap, vault, verify page.
9. Only edit files in your assigned ownership area (below). If a change is needed in another area, in `packages/contracts`, in `apps/api/main.py`, or in `pyproject.toml` / `uv.lock` (Area 3), stop and describe the change instead of making it.
    - Never edit `apps/api/main.py` to add a route. It loads every module in `apps/api/routers/` automatically (ADR-022).
    - Never create or edit Alembic migrations outside Area 3 (`packages/vault/migrations/`). Describe the schema change you need instead.
    - Never edit `CHANGELOG.md`; add a fragment in `changes/` instead.
10. Tests live inside the package they test. Never add a shared top-level tests folder.
11. Never invent facts, numbers, laws, team members or dates. Write `TBD` and add it to `docs/OPEN_QUESTIONS.md`.
12. Any statement about Indian law needs a note that a lawyer must confirm it.

## Ownership areas

| Area | Owns |
|---|---|
| 1. Ingest, Agreement and Release | `packages/ingest`, `apps/api/routers/ingest.py`, `apps/api/routers/agreement.py`, `playbooks/templates/`, `packaging/`, sample chats and demo voice notes |
| 2. AI and ML | `packages/intelligence`, `playbooks/` (except `playbooks/templates/`), `eval/`, `apps/api/routers/analysis.py` |
| 3. Backend, Integrity and Vault | `apps/api/main.py`, `packages/contracts` (steward), `packages/integrity` (except `packages/integrity/anchoring/`), `packages/vault`, `test-vectors/`, `apps/api/routers/vault.py`, `apps/api/routers/export.py`, `.github/workflows/`, `pyproject.toml`, `uv.lock` |
| 4. Frontend and Blockchain | `apps/web`, `apps/verify`, `packages/integrity/anchoring/` |

Shared, changed only by small reviewed pull requests: `packages/contracts`, `docs/`, `.github/`. Dependency files (`pyproject.toml`, `uv.lock`) are owned by Area 3 (Jhashank). Release lead: Hardik. Contracts steward: Jhashank (changes still need all four reviewers). Ask which area you are working in if it is not stated.

## Merge-conflict rules

1. Contracts first: the team agrees `packages/contracts` together on day 1. Later changes are their own small pull request reviewed by all four.
2. One owner per hotspot: `apps/api/main.py` (Area 3), `apps/web/components/` and design tokens (Area 4), dependency files and migrations (Area 3). Request changes instead of editing.
3. Short branches: one feature per branch, merged within 1 to 2 days.
4. Rebase every morning: `git pull --rebase origin dev`.
5. Never commit generated files: reports, caches, model weights, `node_modules`, build output.
6. One file per item: one chat per eval file, one screen per folder, one playbook per YAML file.
7. Formatter and linter run on commit (ruff via pre-commit).
8. The frontend builds against mock data that matches the contracts.
9. Run AI coding tools only inside the member's own area.

## Git

- Branch from `dev`, never from `main`. Pull requests go into `dev`. `main` receives phase releases only.
- Branch names: `feat/<area>-<name>`, `fix/<name>`, `docs/<name>`, `chore/<name>`, `hotfix/<name>` (hotfix branches from `main`).
- Each pull request adds a changelog fragment `changes/<branch-name-with-dashes>.md`.
- Conventional Commits, for example `feat(ingest): parse iPhone export headers`. Small commits.
- Add the attribution line your tool requires to commit messages.

## No hardcoding

1. All configuration comes from one settings module, `apps/api/settings.py` (pydantic-settings, reading `VERIDOC_*` environment variables and `.env`). No paths, ports, model names, URLs or keys in code. Packages receive configuration as arguments; only the API layer reads settings.
2. Business rules live in data, not code: required terms, ambiguity rules, score weights and legal hints in `playbooks/*.yaml`; recap and suggestion wording in `playbooks/templates/`; model choices and SHA-256 hashes in `models/manifest.json`; hardware tier thresholds in settings.
3. Stubs and fixtures are allowed only in tests and in demo mode. Demo mode is the `VERIDOC_DEMO_MODE` setting, never a code edit. Mark every stub `# STUB: replaced by #<issue>` and link a real issue.
4. No logic may depend on sample names, amounts or dates (Raju, Meena, 480, 48000, 15 Nov). They live only in tests, fixtures and eval data.
5. `python scripts/check_hardcoding.py` must pass (pre-commit and CI). A single line may opt out with a comment `hardcoding: ok (<reason>)`; say so in the pull request.

## Definition of done

1. Tests exist and pass, inside the package they test (write tests first).
   - A changelog fragment exists in `changes/`.
2. ruff and mypy pass.
3. Works with the network off.
4. Docs updated (PRD criteria, specs, UX flows as relevant).
5. Threat model row added or updated when a new input or boundary is added.
6. Wording follows `docs/LIMITS.md`.
7. Linked to requirement IDs.
8. `python scripts/check_hardcoding.py` passes (see No hardcoding).

## Commands

Fill the remaining `TBD` when the code lands.

| Task | Command |
|---|---|
| Install | `uv sync` |
| Run | TBD |
| Test | `uv run pytest` |
| Lint | `uv run ruff check .` and `uv run ruff format --check .` |
| Type check | `uv run mypy .` |
| Hardcoding check | `python scripts/check_hardcoding.py` |
| Design token check | `python scripts/check_design_tokens.py` |
| Trust report | TBD |

## Code style

- Python 3.11+, type hints everywhere, mypy clean.
- Pydantic v2 models for all input and output.
- Pure functions in the integrity engine: bytes in, bytes out, no I/O, no clock, no randomness except the salt source passed in.
- No network calls outside the anchoring and share modules.
- Routers are thin; logic lives in packages.
- Frontend: static HTML and JavaScript, no CDN, all assets bundled, every status shows a symbol and a word. Use only the tokens in `apps/web/assets/design-tokens.css` (no raw colours, font sizes or radii); `python scripts/check_design_tokens.py` must pass.
- Match the style of the surrounding code.

## When unsure

Stop and ask. Add the question to `docs/OPEN_QUESTIONS.md` with owner TBD. Do not guess at legal wording, hashing details or contracts.
