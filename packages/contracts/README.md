# packages/contracts

Shared Pydantic v2 models that cross area boundaries. This is the only code shared by both areas of the team. Current version: `CONTRACTS_VERSION` in `version.py` (0.2.0, a draft until Hardik and Abhishek approve PR #40).

Contracts hold shapes only. No business rules: weights, thresholds and required terms live in `playbooks/*.yaml`, wording in `playbooks/templates/`, tier thresholds in `apps/api/settings.py`. The few rules inside models are structural invariants (for example, a value exists exactly when a term is `stated`).

## Layout

| File | Contents |
|---|---|
| `base.py` | `ContractModel` (strict, no extra fields), `FrozenContractModel` (immutable), `requirements()` helper |
| `common.py` | `Uuid`, `Sha256Hex`, `Timestamp`, `DecimalString`, the enums (`TermState` and others), the typed values (`MoneyValue`, `QuantityValue`, `DateValue`, `PartialDateValue`, `EventValue`, `DurationValue`, `TextValue` and the union `TermValue`), `SourceRef`, `PlaybookRef` |
| `chat.py` | `Participant`, `Message`, `VoiceNote`, `Transcript`, `TranscriptSpan` |
| `analysis.py` | `Term`, `AlternativeValue`, `Flag`, `EvidenceScore`, `ScoreBreakdownItem`, `Suggestion` |
| `agreement.py` | `HandshakeQuestion`, `HandshakeAnswer`, `SealedAnswers`, `HandshakeReveal`, `Recap`, `RecapLine`, `EchoCode`, `Confirmation` |
| `record.py` | `AgreedTerm`, `AgreementVersion`, `VersionDiff`, `ReceiptBody`, `Receipt`, `VerifyResult`, `DisputePackManifest`, `ImportRecord`, `LeafRow`, `ReceiptBundle` and their parts |
| `api.py` | `StreamEnvelope` and the event models, `ErrorBody`, `DealSummary` |
| `fixtures/` | Made-up sample deals (clean, ambiguous, contradictory) and API samples; their hashes are computed with `packages/integrity` |
| `CHANGELOG.md` | Every change, with the version bump |

## Conventions

- **Strict.** No type coercion and no unknown fields. Pass real enum members and `datetime` objects in Python; JSON input is parsed with `model_validate_json`.
- **Frozen.** Records that must not change are frozen and use tuples. Only `Term`, `Flag` and `Suggestion` are mutable (they use lists).
- **Ids** are lowercase UUID text. **Hashes** are lowercase hex SHA-256 and are produced only by the integrity engine.
- **Times** carry a UTC offset (kept as given) and whole seconds. **Lengths of time** are integer milliseconds.
- **Money** is integer paise as text (`MoneyValue.paise`). The local model returns whole rupees as an integer; the adapter in `packages/intelligence` multiplies by 100 and writes text. Quantities are whole numbers as text.
- **Dates** with a year are `DateValue`. The model's month-and-day answers are `PartialDateValue` and cannot be confirmed or put in a version until the year is added. Events such as `on_delivery` are `EventValue`.
- **Statuses** of a term are the four words the local model returns: `stated`, `unclear`, `contradicted`, `missing`. The UI says Clear, Ambiguous, Conflict and Missing.
- Each model's docstring and exported JSON Schema list the requirement IDs it serves.

## How to change contracts

The full process is in [docs/DEVELOPMENT_METHODOLOGY.md](../../docs/DEVELOPMENT_METHODOLOGY.md) section 1 and [docs/ONBOARDING.md](../../docs/ONBOARDING.md) section 16. In short:

1. Open an issue labelled `type:contracts` that says what is needed and which areas are affected.
2. Branch from `dev` (`feat/shared-contract-<name>`). Change only `packages/contracts` (and fixtures that must follow). Prefer adding optional fields to renaming or removing.
3. Bump `CONTRACTS_VERSION` and add an entry to `CHANGELOG.md` (breaking change: raise the minor number below 1.0).
4. Update the fixtures and tests. Tests must pass: `uv run pytest packages/contracts`.
5. Open a pull request into `dev` labelled `type:contracts`. **Hardik and Abhishek both approve it.**
6. Feature code that needs the change comes in a later, separate pull request.

## Export JSON Schema

`uv run python scripts/export_contract_schemas.py` writes one schema per model, the three union schemas and an `index.json` (version and requirement IDs) to `out/contract-schemas/`, which is git-ignored.
