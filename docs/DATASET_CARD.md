# Dataset Card

This is a template for documenting a dataset used by VeriDoc, such as the eval set of about 100 labelled chats (see [EVALUATION](EVALUATION.md)). Copy the template once per dataset (for example `docs/datasets/eval-v1.md`) and fill it in. The first card, for the eval set, is not filled yet. Owner: Area 2 (TBD member). No real personal data goes into any dataset in this repository.

Last updated: 2026-10-25
Status: Draft v1

## Template

### 1. Summary
- Name and version:
- Purpose (what it is used for, and what it must not be used for):
- Location in the repository: `eval/chats/`, `eval/labels/`
- Owner and contact: TBD
- Date created and last updated:

### 2. Contents
| Slice | Count | Language | Playbook | Format (Android or iPhone) | Has voice notes |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

- Total chats, total messages, total voice notes, total duration:
- Message length range:
- Terms labelled per chat (average):
- Share of chats by case: clean, ambiguous, contradictory, missing-term, adversarial:
- Held-out split: count and how it is protected (not used for tuning until final reporting):

### 3. Source and consent
- How each chat was created: written by the team (synthetic), written by volunteers, adapted from an anonymised pattern. Real chats are not committed.
- If any contributor wrote chats: who (by role), under what terms, consent recorded where:
- Voice notes: who recorded them, language, consent to use and store:
- Statement: "This dataset contains no real personal data." (or list exceptions and why; any exception needs the lawyer's review, see OPEN_QUESTIONS Q-05)

### 4. Labelling
- Label schema: see EVALUATION section 2 (term state, normalised value, sources, flags)
- Number of labellers and their roles (names not recorded here):
- Process: two labellers per chat, a third settles disagreements
- Agreement rate (fill after labelling):
- Guide version:
- Known label ambiguities:

### 5. Preprocessing
- Normalisation applied (Unicode NFC, digit mapping), if any:
- Anonymisation steps and who checked:

### 6. Distribution and splits
- Training use: none (VeriDoc does not fine-tune models; no fine-tuning claim is made)
- Evaluation use: rules and prompt development splits, held-out split
- Which chats were used to tune rules or prompts, recorded by id:

### 7. Known limitations and biases
- Language coverage gaps (for example few Kannada-English chats):
- Trades and regions not covered:
- Synthetic chats may be cleaner than real ones:
- Voice recording conditions (quiet room, phone microphone):

### 8. Risks and handling
- Privacy risk: low if synthetic; review before adding any real-derived text
- Misuse: not a benchmark of legal outcomes
- Retention and deletion: kept in the repository; remove any item on request

### 9. Maintenance
- How to add a chat: one file per chat in `eval/chats/`, one label file in `eval/labels/`, a pull request reviewed by Area 2
- Versioning: a dataset version is recorded in each trust report
- Change log:

| Date | Version | Change |
|---|---|---|
| TBD | TBD | TBD |
