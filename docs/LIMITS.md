# Honest Limits

This document lists VeriDoc's limits and gives the exact wording that must appear on screen and in other places. The wording is fixed so every screen, document and pitch says the same thing.

Last updated: 2026-10-25
Status: Draft v1

## 1. Limits and exact wording

| # | Limit | Exact wording (English) | Where it appears |
|---|---|---|---|
| L1 | Not legal advice | "Drafting aid, not legal advice." | S6 recap, S10 pack (page one), About, README |
| L2 | No verdict prediction | "VeriDoc does not predict how a court or council will decide." | About, README |
| L3 | Tamper evidence is not authenticity | "This checks that the record was not changed after it was saved. It cannot prove that the original chat export was genuine." | S8, S9 (always visible), README, pack |
| L4 | Does not replace required documents | "VeriDoc does not replace documents that the law requires to be written, stamped or registered. Ask a lawyer if your deal may need one." | About, legal hints, README |
| L5 | Small models are weaker on some languages | "The AI helper is weaker on Hinglish and Kannada-English. Please check every term before you confirm it." | S3 first run, About |
| L6 | Device clock can be wrong | "The time shown comes from this device's clock. It can be wrong until the record is anchored." | S8 |
| L7 | Echo code relies on the export | "The confirmation code relies on the chat export being genuine. It does not show who typed the reply." | S6 (help text), About |
| L8 | Counterparty data and DPDP | "VeriDoc processes the other person's messages on your device. A lawyer should review data-protection duties before public launch." | About; internal PRIVACY |
| L9 | Certificate is a draft | "The certificate is an unsigned draft and must be completed by the person responsible for the device." | S10, pack |
| L10 | Lost passphrase | "If you lose both the passphrase and the recovery key, the data cannot be opened." | S11 |
| L11 | Accuracy figures are targets | "Accuracy figures are targets until a trust report shows measured results." | README, internal docs |
| L12 | Hindi text needs review | "Hindi wording is a draft reviewed by a native speaker." (only after review; until then the UI shows no such claim) | PLAYBOOKS, release checklist |
| L13 | Exports are not encrypted | "Exported files are not encrypted. Share them only with people you trust." | S10 |
| L14 | Safe mode | "Safe mode: rules only. The AI helper is off." | Banner |

## 2. Hindi wording (draft)

Draft translations; native-speaker review is required before use.

| # | Hindi |
|---|---|
| L1 | मसौदा बनाने में सहायता, कानूनी सलाह नहीं। |
| L3 | यह जाँच बताती है कि रिकॉर्ड सहेजने के बाद बदला नहीं गया। यह साबित नहीं कर सकती कि मूल चैट एक्सपोर्ट असली था। |
| L6 | दिखाया गया समय इसी डिवाइस की घड़ी का है। जब तक रिकॉर्ड एंकर न हो, यह गलत हो सकता है। |

## 3. Wording rules for all documents and UI

| Use | Do not use |
|---|---|
| tamper-evident | any word claiming the record cannot be changed |
| court-ready evidence package | any claim that output is a legal instrument |
| drafting and record-keeping aid | advice, opinion, or similar words about the law |
| target | any claim of accuracy or speed before it is measured |
| "the record was not changed after it was saved" | "proves the chat is real" |
| "may need a registered document; ask a lawyer" | "you must register" or "you need not register" |

Claims about superiority, novelty or certainty are not used. Anything about Indian law carries a note that a lawyer must confirm it.

## 4. Where the limits live in the product

- S3: first-run notice (L5).
- S6: disclaimer line and echo-code help (L1, L7).
- S8 and S9: authenticity limit (L3), clock note (L6).
- S10: disclaimer first (L1, L9, L13).
- S11: About and limits panel with all rows (L1 to L14), and the lost-passphrase warning (L10).
