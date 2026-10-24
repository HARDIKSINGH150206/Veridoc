# Model Card

This is a template for documenting each model VeriDoc runs locally: the extraction language models for each hardware tier and the speech models. Copy it once per model into the table at the end and fill in the details after the benchmark. Exact models are `TBD` pending benchmarks (OPEN_QUESTIONS Q-13, Q-14). Owner: Area 2 (Abhishek). No accuracy or speed figure is entered until a trust report measures it. Model weights are never committed; only names and SHA-256 hashes go into `models/manifest.json`.

Last updated: 2026-10-25
Status: Draft v1

## Template (one per model)

### 1. Identity
- Model name and version: TBD
- Role: extraction (rules refinement) or speech to text
- Tier: High (about 7B), Default (about 3B), Low (about 1.5B), speech small, speech base
- Source (official page) and licence: TBD (check that the licence allows our use and redistribution on a USB stick)
- File name, size and quantisation: TBD
- SHA-256 (also in `models/manifest.json`): TBD
- Runtime: llama.cpp via llama-cpp-python, or faster-whisper

### 2. Intended use
- Used for: proposing terms in the fixed schema from chat text and transcripts; transcribing voice notes at import.
- The model only suggests. It never writes to the vault or hash path. A person confirms every term.
- Not used for: legal advice, predicting outcomes, judging whether a chat is genuine, writing recaps, sending messages.

### 3. Inputs and outputs
- Input: normalised message windows as data, plus the playbook term list, inside a fixed prompt.
- Output: JSON constrained by the schema in AI_SPEC section 4; speech models output segments with times and confidence.
- Network use: none.

### 4. Hardware and speed
| Laptop | RAM | CPU | Tier | Load time | Refinement time | Voice time (30 s) | Date | Commit |
|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Targets (not measured): model ready under 60 s; AI refinement under 10 s on an 8 GB laptop; a 30-second voice note in about 15 s on an 8 GB laptop.

### 5. Measured quality
Numbers come only from a named trust report.

| Slice | Precision | Recall | F1 | Grounding failures | Needs-review rate | Report date and commit |
|---|---|---|---|---|---|---|
| English | TBD | TBD | TBD | TBD | TBD | TBD |
| Hinglish | TBD | TBD | TBD | TBD | TBD | TBD |
| Kannada-English | TBD | TBD | TBD | TBD | TBD | TBD |
| Voice (WER) | TBD | | | | | TBD |

Target: field-level extraction at or above 90% on the eval set (target, to be measured).

### 6. Safety tests
| Test | Result | Report |
|---|---|---|
| Prompt-injection fixtures leave terms and flags unchanged | TBD | TBD |
| Grounding: ungrounded terms reaching the record | TBD | TBD |
| Rules versus model disagreement marked needs review | TBD | TBD |
| Model hash mismatch gives safe mode | TBD | TBD |

### 7. Limits and known weaknesses
- Small models are weaker on Hinglish and Kannada-English.
- Noisy audio lowers transcription quality.
- Sarcasm, quoted text and long negotiations can mislead extraction.
- Control: grounding, needs-review marking, human confirmation, safe mode.

### 8. Base versus fine-tuned (only if fine-tuning was run, ADR-023)
| Model | Held-out F1 | Grounding failures | Injection fixtures changed | Worst language slice | Report date and commit |
|---|---|---|---|---|---|
| Base | TBD | TBD | TBD | TBD | TBD |
| Fine-tuned | TBD | TBD | TBD | TBD | TBD |

The fine-tuned model ships only if it passes the gate in ADR-023. If it does not, state that here and keep the base model.

### 9. Decision record
- Why this model was chosen for this tier (benchmark summary, link to the ADR in DECISIONS.md): TBD
- Alternatives tested: TBD
- Reviewer: TBD

### 10. Change log
| Date | Change | Commit |
|---|---|---|
| TBD | TBD | TBD |

## Model register

| Role | Tier | Model | Card | Status |
|---|---|---|---|---|
| Extraction | High | TBD | not written | pending benchmark |
| Extraction | Default | TBD | not written | pending benchmark |
| Extraction | Low | TBD | not written | pending benchmark |
| Speech | small | faster-whisper small (version TBD) | not written | pending benchmark |
| Speech | base | faster-whisper base (version TBD) | not written | pending benchmark |
