Rules engine, local AI runner, flags, score, suggestion, speech runner (speech/). Owner: Area 2. Tests go in packages/intelligence/tests/.

## model_adapter/ (issue #63, Q-64)

Turns the local model's JSON (LLM_HANDOVER.md section 5) into contract `Term`s. Output only: it never writes to the vault, imports the vault or the hashing code, and never confirms a term (every term is origin `ai`, `confirmed_at` null).

| File | Role |
|---|---|
| `output.py` | `ModelOutput`, `TermOutput`, `MalformedTerm`, `parse_model_output` (raises `ModelOutputError` only when the reply is not the expected top-level object) |
| `chat.py` | `ChatContext` and `numbered_chat`: the prompt's user message, built from the same message list the mapping uses |
| `mapping.py` | `map_output(output, chat) -> list[Term]` |
| `adapter.py` | `ModelAdapter` protocol, `FakeModelAdapter`, `LocalModelAdapter` (not built, issue #69), `build_adapter(mode, recordings_dir)` |
| `data/` | prompt line format, term kinds, known unclear reasons and event names (data, so playbook alignment changes files, not code) |

Mapping rules (acceptance criteria of #63 and #64):

- Dates `MM-DD` become `PartialDateValue` `--MM-DD`; `on_delivery` and `on_completion` become `EventValue`; an impossible date needs review.
- Whole rupees become `MoneyValue` paise text (rupees times 100). `quantity` and `revisions` integers become `QuantityValue` with `unit` null.
- Anything that does not fit (float or missing money value, a status outside the four, wrong types) becomes an `unclear` term with no value, `needs_review` true, confidence low and the original wording in `raw`. Nothing raises.
- Message numbers are 1-based positions in the numbered chat, which includes system, media-omitted, deleted and voice-note lines. A voice note's line is its transcript text; the quote is located in the transcript spans to give `VoiceSourceRef.start_ms` and `end_ms` (a quote across spans covers both). A quote that is not found keeps a message source and needs review.
- Safety net (handover section 12): a quote that is not in its message (or in the sender's name, which the model may quote for party terms) is not grounded; a money or quantity value that is not among the numbers in its own quote is flagged; an unclear money term whose quote holds a number is flagged. Values are never changed, only flagged. The second-mention check needs the rules engine and is not built (issue #69).
- Confidence is `medium` for a term that passes these checks and `low` otherwise; `high` is reserved for rules and AI agreeing. Term ids are deterministic from the deal id and the key.

`VERIDOC_MODEL_MODE=fake|local` picks the adapter (default `fake`; `local` raises `NotImplementedError`). Recorded outputs are in `fixtures/recordings/`, including the two real mistakes of the v1 model: `unit_price` 48000 against the quote "480 each ok?", and the advance in "done sent 48000" missed.

Open: Q-62 (playbook keys), issue #69 (local adapter).
