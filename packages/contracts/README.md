# packages/contracts

Shared Pydantic v2 models that cross area boundaries. This is the only code shared by all four areas. Current version: `CONTRACTS_VERSION` in `version.py` (0.1.0, draft until all four members approve).

Contracts hold shapes only. No business rules: weights, thresholds and required terms live in `playbooks/*.yaml`, wording in `playbooks/templates/`, tier thresholds in `apps/api/settings.py`.

## Layout

| File | Contents |
|---|---|
| `base.py` | `ContractModel` (strict, no extra fields), `FrozenContractModel` (immutable), `requirements()` helper |
| `common.py` | Enums, `Sha256Hex`, `Timestamp`, `SourceRef` (message id, or voice note with start and end seconds), `PlaybookRef` |
| `chat.py` | `Participant`, `Message`, `VoiceNote`, `Transcript`, `TranscriptSpan` |
| `analysis.py` | `Term`, `AlternativeValue`, `Flag`, `EvidenceScore`, `ScoreBreakdownItem`, `Suggestion` |
| `agreement.py` | `HandshakeQuestion`, `HandshakeAnswer`, `SealedAnswers`, `Recap`, `RecapLine`, `EchoCode`, `Confirmation` |
| `record.py` | `AgreementVersion`, `VersionDiff`, `Receipt`, `VerifyResult`, `DisputePackManifest` and their parts |
| `fixtures/` | Made-up sample deals (clean, ambiguous, contradictory) that validate against the models |
| `CHANGELOG.md` | Every change, with the version bump |

## Conventions

- **Strict.** No type coercion and no unknown fields. Pass real enum members and `datetime` objects in Python; JSON input is parsed with `model_validate_json`.
- **Frozen.** Records that must not change (messages, transcripts, receipts, versions, sealed answers) are frozen. `Term`, `Flag` and `Suggestion` are mutable until they are confirmed or resolved.
- **Tuples.** Sequences in frozen models are tuples (use `tuple(...)` when building them in Python).
- **Times** are timezone-aware (a UTC offset is required).
- **Hashes** are lowercase hex SHA-256 (64 characters) and are produced only by the integrity engine.
- **Money** is integer paise in a string; **dates** in terms are ISO 8601 strings; quantities are plain integers in a string. Details: `docs/INTEGRITY_SPEC.md` section 4.
- Each model's docstring and exported JSON Schema list the requirement IDs it serves.

## How to change contracts

The full process is in [docs/DEVELOPMENT_METHODOLOGY.md](../../docs/DEVELOPMENT_METHODOLOGY.md) section 1 and [docs/ONBOARDING.md](../../docs/ONBOARDING.md) section 16. In short:

1. Open an issue labelled `type:contracts` that says what is needed and which areas are affected.
2. Branch from `dev` (`feat/shared-contract-<name>`). Change only `packages/contracts` (and fixtures that must follow, agreed with their owners). Prefer adding optional fields to renaming or removing.
3. Bump `CONTRACTS_VERSION` and add an entry to `CHANGELOG.md` (breaking change: raise the minor number below 1.0).
4. Update the fixtures and tests. Tests must pass: `uv run pytest packages/contracts`.
5. Open a pull request into `dev` labelled `type:contracts`. All four members review it; the steward (Jhashank) shapes it first.
6. Feature code that needs the change comes in a later, separate pull request.

## Export JSON Schema

`uv run python scripts/export_contract_schemas.py` writes one schema per model and an `index.json` (version and requirement IDs) to `out/contract-schemas/`, which is git-ignored. The frontend can read these without importing Python.
