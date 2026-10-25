# Contracts changelog

Every change to `packages/contracts` is listed here and bumps `CONTRACTS_VERSION` in `version.py`. Versions follow semantic versioning while below 1.0: a breaking change raises the minor number, an addition or fix raises the patch number.

## 0.2.0

Resolves the open points of PR #40: Jhashank's steward review (D1 to D7), the 15 suggested answers, Q-61 and the model handover questions (`LLM_HANDOVER.md`). Breaking changes (this is still a draft below 1.0, so they raise the minor number).

- **Statuses match the local model.** `TermState` is now `stated`, `unclear`, `contradicted`, `missing` (was clear, ambiguous, missing, conflict). The UI words and symbols stay Clear, Ambiguous, Conflict, Missing.
- **Typed values** (answer 2): `Term.value` and the other value fields are a discriminated union `TermValue` of `MoneyValue` (integer paise as text), `QuantityValue`, `DateValue` (full date), `PartialDateValue` (month and day, no year, as the model returns it), `EventValue` (on_delivery and so on), `DurationValue` and `TextValue`. `value_type`, `unit` and the string `value` are gone. The model adapter turns the model's integer rupees into paise text.
- **Term rules:** a value exists exactly when the state is `stated`; an `unclear_reason` only when `unclear`; a missing term has no sources; only a stated term with a concrete value can be confirmed (answer 4). `Term` also gets `confirmed_by`. Mutable models use lists (answer 1).
- **D1:** `Recap` has `body_text` (no code line) and `text` (body plus code line). `recap_hash` and the echo code derive from the content without the code; `text` and `echo_code` are not hashed.
- **D2:** `Receipt` is an envelope `{body: ReceiptBody, receipt_hash}`; the hash covers the body only.
- **D3 and Q-61:** integer milliseconds everywhere: `TranscriptSpan.start_ms`/`end_ms`, `VoiceNote.duration_ms`, `VoiceSourceRef.start_ms`/`end_ms`.
- **D4:** contract field names are final (`sender_id`, `origin`, `attachment_hash`, `version_n` everywhere; `AgreementVersion.n` is now `version_n`). INTEGRITY_SPEC adopts them.
- **D5:** new frozen `AgreedTerm` (`key`, `value`, `sources`, `confirmed_by`, `confirmed_at`) replaces mutable terms inside `AgreementVersion`. `Confirmation` gains `deal_id`, `version_n` and `code`; its failure reasons are `code_mismatch`, `wrong_sender`, `recap_changed`, `malformed_reply`, `declined`.
- **D6:** `Timestamp` must carry a UTC offset and whole seconds. The hashed text form is `YYYY-MM-DDTHH:MM:SS+HH:MM`, never `Z` (INTEGRITY_SPEC section 2). The function and vectors in both languages follow in a separate issue.
- **D7:** `FirstDifference.kind` has one value per leaf type plus `import_record` and `chain_link`. New `LeafRow`, `ImportRecord`, `BundleFile` and `ReceiptBundle` models cover the bundle (answer 10).
- **Answers 3, 5, 6, 7, 8, 9, 12, 13, 14:** separate unit price and total terms (the playbook defines the keys; fixtures use the model's `unit_price` and `total_amount`); `Flag.cross_modal` is a computed property and `Flag` holds `reason_code` plus `reason_params` instead of prose; `VoiceNote` references its transcript by `transcript_id`; new `HandshakeReveal` and `HandshakeRevealRow`; new `StreamEnvelope` and the event models, `ErrorBody` and `DealSummary`; all ids are lowercase UUID text; `deal_id` stays on every record; `kn` stays in `Language`.
- Fixtures regenerated: hashes in them are computed with `packages/integrity` (the recap hash and echo code no longer depend on the code).

## 0.1.0

First draft for team review (issue #4). Nothing here is agreed until all four members approve the pull request.

- Chat input: `Participant`, `Message`, `VoiceNote`, `Transcript`, `TranscriptSpan`.
- Evidence references: `SourceRef` (`MessageSourceRef` or `VoiceSourceRef`), `PlaybookRef`.
- Analysis: `Term`, `AlternativeValue`, `Flag`, `EvidenceScore`, `ScoreBreakdownItem`, `Suggestion`.
- Agreement: `HandshakeQuestion`, `HandshakeAnswer`, `SealedAnswers`, `Recap`, `RecapLine`, `EchoCode`, `Confirmation`.
- Record: `AgreementVersion`, `VersionDiff`, `TermDiffRow`, `Receipt`, `ChainLink`, `Anchor`, `VerifyResult`, `VerifyCheck`, `FirstDifference`, `DisputePackManifest`, `PackPart`.
- Fixtures for a clean, an ambiguous and a contradictory sample deal.
