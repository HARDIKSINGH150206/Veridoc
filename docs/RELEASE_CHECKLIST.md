# Release Checklist

This checklist lists what must pass before `dev` is merged into `main` at the end of a phase. The release lead (Hardik, Area 4) runs it with the other three members during the integration hour. Phase-specific gates are in [PHASES](PHASES.md); this list is the common part. Steps for the merge and tag are in [GIT_WORKFLOW](GIT_WORKFLOW.md) section 5.

Last updated: 2026-10-25
Status: Draft v1

Release lead: Hardik. Phase and tag: fill in per release (`v0.N-phaseN`).

## 1. Before you start

- [ ] All pull requests meant for this phase are merged into `dev`
- [ ] `dev` is frozen for the checklist run (no other merges)
- [ ] The phase gate in PHASES.md is read aloud and each item is checked below
- [ ] Open issues labelled `blocked` or `type:contracts` for this phase are resolved or consciously deferred (noted)

## 2. Automated checks on `dev`

- [ ] CI is green: ruff lint and format, mypy, pytest for every package
- [ ] Contract tests pass for all areas
- [ ] Integrity tamper tests pass (all seven cases)
- [ ] Python and JavaScript test vectors match (`test-vectors/integrity/`)
- [ ] `python scripts/check_hardcoding.py` passes
- [ ] gitleaks secret scan passes; pip-audit has no unaddressed high findings
- [ ] Insert-only trigger test passes after `alembic upgrade head` on a fresh vault
- [ ] `python3 scripts/check_folder_tree.py` prints `OK`

## 3. Manual checks

- [ ] A clean clone of `dev` installs and runs on Windows, macOS and Linux (or the subset available, noted)
- [ ] The app works with the network off; every screen loads with the network blocked
- [ ] The sample chats (clean, ambiguous, contradictory, voice) produce the expected flags
- [ ] Safe mode works: wrong model hash gives rules-only mode and a visible reason
- [ ] The verify page opens by double-click with the network off, shows UNCHANGED for a good bundle and ALTERED, naming the first item, for a changed one
- [ ] Every status on screen shows a symbol and a word
- [ ] Keyboard-only walk through the main flow works
- [ ] Hindi text renders with no missing glyphs (when Hindi is in this phase)

## 4. Integrity and AI safety

- [ ] No change to hashing, Merkle, chain, echo code or verify without a matching INTEGRITY_SPEC and vector update
- [ ] The intelligence package imports nothing from the vault or hash path (test passes)
- [ ] Grounding and injection tests pass
- [ ] Logs checked: no message content, transcripts or identifiers

## 5. Documents and wording

- [ ] PRD acceptance criteria for this phase are met and referenced in the pull requests
- [ ] Docs updated for anything that changed; THREAT_MODEL rows added for new inputs or boundaries
- [ ] Wording check: tamper-evident wording only, "court-ready evidence package", "not legal advice", targets labelled as targets
- [ ] Any number in README or slides comes from a named trust report with date and commit
- [ ] OPEN_QUESTIONS updated: closed items moved to Resolved; new TBDs added
- [ ] Changelog fragments combined into `CHANGELOG.md` and the fragments deleted
- [ ] The "Current phase" line in PHASES.md updated

## 6. Repository hygiene

- [ ] No secrets, `.env` files, model weights, real chats, generated reports or large files in the diff
- [ ] `models/manifest.json` has names and hashes only
- [ ] `uv.lock` matches `pyproject.toml`
- [ ] Branches already merged are deleted

## 7. Release

- [ ] Pull request `dev` into `main` opened and merged with a merge commit
- [ ] Annotated tag `v0.N-phaseN` created on `main` and pushed
- [ ] Pull request `main` into `dev` merged to sync the merge commit
- [ ] Team told in the chat; everyone runs `git pull --rebase origin dev`

## 8. Extra items for the demo build (Phase 4, tag `v0.4-phase4`)

- [ ] [DEMO_DAY_RUNBOOK](DEMO_DAY_RUNBOOK.md) rehearsed twice end to end, under four minutes
- [ ] Pendrive built from the tagged commit; run on a second laptop with the network off
- [ ] Windows default antivirus did not block the launcher
- [ ] Benchmarks on three laptops recorded in PERFORMANCE.md with date and commit
- [ ] Trust report generated; accuracy and speed numbers in slides match it
- [ ] Recorded backup video made from this build
- [ ] The SHA-256 of `verify.html` is recorded in the release notes
- [ ] All MVP acceptance criteria in the PRD pass
