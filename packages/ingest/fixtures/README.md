# Synthetic import samples

Issue #12; FR-IMP-007 and FR-VOI-001. All participants, messages, amounts and dates
are fictional test data authored for VeriDoc. No real WhatsApp export, personal
recording or user data was used. Asha supplies shirts; Bilal buys them.

Each `.txt` chat uses UTF-8, LF line endings and the simple Android-style
`DD/MM/YYYY, HH:MM - Sender: text` export format. One message occupies one line.
The fixture timezone assumption is Asia/Kolkata; the raw exports deliberately
have no offset, as in WhatsApp exports. These are raw inputs, not shared-contract
objects. Parsed Message fixtures and their contract validation belong to #13.

| Sample | Messages | Intended result once analysis exists |
|---|---|---|
| `clean.txt` | 6 | Explicit parties, scope, quantity, price, advance, delivery, final payment and late-penalty terms. Both parties agree. "No late penalty" is an explicit value, not Missing. |
| `ambiguous.txt` | 5 | Delivery is Ambiguous ("next week"); final payment and late penalty are Missing. The arithmetic balance does not establish when it is due. |
| `contradictory.txt` | 5 | Unresolved total-price Conflict: 50,000 versus 45,000 INR. Text delivery is 15 November 2026; the attached voice says 22 November 2026. |

The clean sample's acknowledgements are conversation evidence, not automatic
user confirmation in VeriDoc. No sample supplies a score, fabricated receipt or
integrity hash. Analysis assertions are future integration work with Area 2;
the tests here check the inputs only. PR #40 is still a draft dependency for #13.

## Voice provenance and regeneration

`delivery-22-nov.wav` is synthetic English speech generated offline with Windows
System.Speech, **Microsoft Zira Desktop (en-US)**, rate -1, volume 100, mono
16-bit PCM at 16,000 Hz. `delivery-22-nov.transcript.txt` is its exact input script,
not a model transcription or a human-reviewed gold transcript. The voice is
fictional Asha's message at line 4 of `contradictory.txt`.

To regenerate on Windows with that voice installed, from the repository root:

```powershell
powershell -NoProfile -File packages/ingest/fixtures/generate_voice.ps1
```

The script overwrites only the adjacent WAV. Windows voice versions may change
the waveform; byte-for-byte reproducibility is not claimed. Playback and tests
use the committed WAV and need no speech engine, model download or network.
This short English clip supports the Phase 0 fixture task; it does not satisfy
the later 30-second Hindi transcription benchmark in FR-VOI-001. Transcription
accuracy and audible pronunciation still need review with Area 2's runner.

## Handoff to Abhishek: eval ownership

`eval/chats/` and `eval/labels/` belong to Area 2. Request: register these three
samples in the agreed eval layout and add same-basename gold label files under
`eval/labels/` (FR-IMP-007). Keep source references aligned with #13's Message
IDs after contracts are agreed. Until then, these are one-based raw chat lines:

| Sample | Evidence for labelling |
|---|---|
| clean | Scope/quantity/unit and total price: lines 1–2. Advance, balance timing and delivery: line 3. Explicit no-penalty term: line 4. Acknowledgements/payment: lines 5–6. |
| ambiguous | Scope/quantity/price: lines 1–2. Advance and ambiguous delivery: line 3. Advance paid/received: lines 4–5. No sources exist for final-payment timing or late penalty. |
| contradictory | Total-price alternatives: lines 1–2. Text delivery: line 1. Voice attachment: line 4. Unresolved status: line 5. Listen to the audio and annotate the actual date span before assigning voice time ranges. |

Decide unit-price versus total-price keys with the PR #40 review. Do not treat
the proposed contract changes as merged, or invent transcript confidence/time
ranges. The eval integration and gold labels remain pending Area 2's change.

Run the input checks with `uv run pytest packages/ingest/tests/test_sample_fixtures.py`.
