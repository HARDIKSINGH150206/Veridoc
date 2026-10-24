# Contracts changelog

Every change to `packages/contracts` is listed here and bumps `CONTRACTS_VERSION` in `version.py`. Versions follow semantic versioning while below 1.0: a breaking change raises the minor number, an addition or fix raises the patch number.

## 0.1.0

First draft for team review (issue #4). Nothing here is agreed until all four members approve the pull request.

- Chat input: `Participant`, `Message`, `VoiceNote`, `Transcript`, `TranscriptSpan`.
- Evidence references: `SourceRef` (`MessageSourceRef` or `VoiceSourceRef`), `PlaybookRef`.
- Analysis: `Term`, `AlternativeValue`, `Flag`, `EvidenceScore`, `ScoreBreakdownItem`, `Suggestion`.
- Agreement: `HandshakeQuestion`, `HandshakeAnswer`, `SealedAnswers`, `Recap`, `RecapLine`, `EchoCode`, `Confirmation`.
- Record: `AgreementVersion`, `VersionDiff`, `TermDiffRow`, `Receipt`, `ChainLink`, `Anchor`, `VerifyResult`, `VerifyCheck`, `FirstDifference`, `DisputePackManifest`, `PackPart`.
- Fixtures for a clean, an ambiguous and a contradictory sample deal.
