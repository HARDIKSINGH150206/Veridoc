# Launcher and packaging (Area 1)

Issue #15 adds the Windows development launcher for Phase 0. It starts the existing
API and opens the bundled S1 layout preview. The screens still show placeholders;
the complete import-to-receipt flow belongs to #29. Requirements: NFR-PERF-001,
NFR-PORT-001; loopback binding also follows NFR-SEC-004.

## First run on Windows

Install Python 3.11+ and uv, clone the repository, then run `uv sync --locked` in
the repository folder. This setup step needs dependencies available in the cache
or internet access. Then double-click `packaging/START.bat`, or run:

```powershell
.\packaging\START.bat
```

The batch file locates `.venv\Scripts\python.exe` relative to itself, including
when the checkout path contains spaces. If setup is missing it prints an
instruction and exits with an error; startup never installs or downloads anything.
Keep the terminal open; press Ctrl+C to stop the server. The batch file preserves
the launcher's exit code. From an existing terminal, errors remain visible.

The equivalent Python entry point is `uv run --locked --offline python packaging/launcher.py`.
Do not use `python -m packaging`: the installed dependency has that module name.

## Configuration and behaviour

The API creates its existing Settings object from `VERIDOC_*` environment variables
and the repository's `.env`. The launcher uses that object; it introduces no
separate configuration reader. The working directory is set to the checkout root
before loading the API so `.env` resolution does not depend on where it was started.

- The host comes from Settings and is restricted there to loopback.
- Leave `VERIDOC_PORT` unset for an OS-selected free port, or set it to the desired
  port. An occupied configured port fails instead of silently choosing another.
- The bound socket is retained through startup; there is no find-close-rebind race.
- Only `apps/web` is served at `/ui`; the initial page is its S1 screen. These are
  bundle-layout paths, resolved relative to the checkout, not machine-specific paths.
- Browser opening happens after application startup and socket readiness. If it
  fails, the terminal prints the local address for manual opening.
- HTTP access logging is disabled so request paths/identifiers do not enter logs.
  Launcher error messages omit raw exceptions and environment values.
- The launcher makes no external network requests. Assets and API are local.

This is the one-OS development launcher. Portable runtimes, hardware detection,
macOS/Linux entry points and USB benchmarks are later work. The under-15-second
startup figure remains a target; this preview does not establish MVP usability.

## Checks and owner handoffs

Run `uv run pytest packaging/tests/test_launcher.py` explicitly. Tests cover the
real local HTTP server, UI/asset serving, traversal rejection, port conflicts,
browser fallback, shutdown, safe errors and the Windows batch entry point.

Requests for Area 3 (Jhashank; Hardik while covering Area 3):

1. Add `packaging` to pytest's `testpaths` in `pyproject.toml`. Until then the
   default `uv run pytest` and CI do not collect these tests; run them explicitly.
   Keep the existing package/app/script paths. Add Windows CI coverage for the
   batch tests when the team expands the current Linux-only job.
2. Review/update THREAT_MODEL T16/T17 for the launcher serving the bundled web
   subtree on the same loopback server. Traversal tests and disabled access logs
   are included here. Existing API authentication/origin controls remain Area 3
   work; mounting the preview is not a claim those controls are implemented.

These shared files were not edited in this Area 1 change. No hashing, vault
storage, contracts, model loading or frontend files are changed by the launcher.
# Contract-flow harness (#16)

`packaging/tests` is part of the default pytest paths. The harness imports messages
through the real demo route, passes them to a test-only analysis adapter, requires
a simulated human confirmation and obtains a contract-validated fake receipt.
Its sentinel hashes are computed from a test label, not from evidence; the receipt
is marked `test-only-fake-not-verifiable` and is never written to the vault.

The harness uses the merged contracts v0.2.0 (Term, Receipt envelope). Replace the fake adapters with #30 and #31 once their ports
are agreed, then connect the real screen flow from #32 and the offline verifier.
The test does not establish that those areas are integrated or that #29 passes.

## Remaining owner handoffs

- Hardik: provide the record adapter (#31) and add Windows CI.
- Abhishek: provide the analysis adapter (#17/#30), and finish the eval labels
  handoff described in `packages/ingest/fixtures/README.md` (#12/#18).
- Hardik: connect S1-S3 and receipt display to the adapters (#27/#32), review the
  shared threat-model documentation for demo/static-serving boundaries.
- Team: verify a clean clone on macOS and Linux and the full browser path before
  closing #29; current execution evidence covers Windows only. #3 also needs
  human account/team setup and each person's first reviewed, merged PR.

