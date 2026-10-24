# Privacy

This document describes how VeriDoc handles personal data: the local-first default, masking, logging, sharing, deletion and DPDP notes. It is a design statement, not a legal opinion. A lawyer must review it before public launch.

Last updated: 2026-10-25
Status: Draft v1

## 1. Principles

1. Local first. Chats, voice notes, transcripts, terms and receipts stay on the user's device.
2. Offline by default. Network use exists only in two optional modules: anchoring and share link.
3. Only hashes leave for anchoring. Only ciphertext leaves for sharing.
4. The AI runs on the device. There is no cloud AI.
5. Logs hold no content.
6. The user decides what is exported.

## 2. Data handled

| Data | Contains | Where it lives | Leaves the device when |
|---|---|---|---|
| Chat messages | Names, phone-linked display names, prices, bank details | Encrypted vault | Never by default; in an export or share the user chooses |
| Voice notes and transcripts | Voices, spoken details | Encrypted vault | Same |
| Terms, versions, recaps | Deal facts | Encrypted vault | Same; the recap text is copied to WhatsApp by the user |
| Hashes and receipts | Hashes only | Vault; bundle | In the bundle or anchored (hash only) |
| Passphrase | Secret | Never stored; only used to derive a key | Never |
| Recovery key | Secret | Printed by the user | Never |
| Logs | Counts, durations, error codes | Local log file | Never |

The counterparty's data (their messages and voice) is processed too. See section 8.

## 3. Local-first behaviour

- The backend binds to 127.0.0.1.
- The UI loads no CDN assets; fonts, CSS and JS are bundled.
- The verify page makes no network request.
- A permanent line on S2 says "This chat stays on this device. Nothing is uploaded."

## 4. Privacy mask (P1)

The mask applies to **exports, shares and any cloud call**. It does not apply to local processing, which needs the real values.

| Item | Detection | Replacement |
|---|---|---|
| Bank account number | 9 to 18 digits near account words | `[ACCOUNT_n]` |
| Card number | 13 to 19 digits, Luhn check | `[CARD_n]` |
| Aadhaar | 12 digits, Verhoeff checksum | `[AADHAAR_n]` |
| PAN | `AAAAA9999A` pattern | `[PAN_n]` |
| IFSC | `AAAA0AAAAAA` pattern | `[BANK_CODE_n]` |
| UPI ID | `name@bank` pattern | `[UPI_n]` |
| OTP or password | 4 to 8 digits or a string near words like OTP, password, PIN | `[SECRET_n]` |

Rules:
1. Never mask amounts or dates.
2. Replacement tokens are stable inside an export (the same account is always `[ACCOUNT_1]`).
3. Masking is shown in a preview before export (S10).
4. Masked parts still verify: the receipt holds the original leaf hashes; the export carries the masked text plus the salt and leaf hash so a holder of the original can verify it. A verifier without the original sees "masked, not verifiable".
5. Mask patterns will miss some cases. The user reviews the preview.

## 5. Logging rules

| Allowed | Not allowed |
|---|---|
| Event names, counts, durations, error codes, model tier | Message text, transcripts, names, phone numbers, terms values, file names from the user |

Developers must not add content to logs, debug prints or exception messages. A test greps log output for fixture strings.

## 6. Sharing (P1)

| Feature | Behaviour |
|---|---|
| Selective disclosure | The user chooses messages; the pack shows only those with inclusion proofs; others appear as "not disclosed" |
| Share link | Bundle encrypted on the device; key in the URL fragment so it never reaches the server; view-only; expiry; revoke; access log |
| Server | Holds ciphertext, expiry and the access log; never the key |

Neither exists in the MVP. Recipients see exactly what the pack contains.

## 7. Deletion and crypto-shredding

- "Delete deal" removes the deal's wrapped key and its evidence files, and records an audit event without content.
- Without the key the remaining encrypted rows are unreadable.
- A bundle or dispute pack already exported stays with whoever has it; VeriDoc cannot recall it.
- Deleting the whole vault means deleting the vault folder; the recovery key becomes useless with it.

## 8. DPDP notes

Everything here needs a lawyer's confirmation before public launch.

1. VeriDoc processes personal data of people who did not install it (the counterparty). The legal basis, notice and consent approach are `TBD`.
2. Local-first processing means the product team does not receive the data, which may change who is the data fiduciary and who is the processor. Lawyer to confirm.
3. Retention and deletion rights of the counterparty: how to handle a request to delete their messages from a user's vault is `TBD`.
4. Children's data: out of scope; not targeted.
5. Cross-border transfer: none by default; anchoring sends only hashes.
6. Breach handling: a lost stick is protected by encryption; process `TBD`.

## 9. User-facing privacy copy

- S2: "This chat stays on this device. Nothing is uploaded."
- S11 anchoring: "Sends only a hash, never chat content."
- S10 export warning: "Exported files are not encrypted. Share them only with people you trust."
- About: "VeriDoc processes the other person's messages on your device. Tell them how you keep their records." (wording `TBD`, lawyer to confirm)
