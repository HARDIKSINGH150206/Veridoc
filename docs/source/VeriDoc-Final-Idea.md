> **Note (2026-10-25):** This document is a source input and is superseded by `docs/PRD.md` wherever the two differ. Known differences: confirmation uses an echo code, not a one-tap link; Kannada recap is P1; voice-to-text (faster-whisper) is MVP; model choices follow hardware tiers and are TBD; Evidence Strength follows the PRD formula (FR-SCO-001); the integrity layer is written from scratch. See `docs/OPEN_QUESTIONS.md`. The text below is unchanged.

# Vachan: Handshake → Recap → Receipt

*Working name ("Vachan" means promise). Problem statement: LS-06, From Handshake to Contract (Informal Agreements). Rename it to whatever your team prefers.*

**Tagline:** Others explain the dispute after it happens. We help you avoid it while you are still chatting.

---

## 1. The pain point

A large share of small-business dealings in India happen over WhatsApp chats, voice notes and verbal promises. Shopkeepers, freelancers, tutors, contractors, landlords and small suppliers all work this way.

- **No clean agreement exists.** Price is in one chat, the revised deadline is in a voice note, and the payment term was never said.
- **Chats are scattered and ambiguous.** "Next week", "approx 50k" and "will pay soon" are not provable terms.
- **Formal contracts feel awkward.** Asking a long-standing customer to sign something feels legalistic, expensive and slow, so owners avoid it.
- **The pain shows up too late.** The gap is discovered only when someone refuses to pay or deliver, and by then the missing terms cannot be recovered.
- **Evidence is weak.** Chat exports can be edited, and nobody can prove that a record was unchanged since the day it was made.

The real problem is not a missing contract template. It is the **social friction** of asking for one, plus the fact that nobody tells you what is missing while the conversation is still going on.

---

## 2. Our solution in one flow

**Handshake → Recap → Receipt**

1. **Handshake:** the two parties chat as usual (pasted or uploaded WhatsApp export, voice notes, or the built-in chat simulator).
2. **Live analysis:** a local AI model extracts the key terms, links each one to its source message, and shows what is missing or unclear.
3. **Smart next message:** the tool suggests the one friendly reply that closes the biggest gap, for example *"Just to confirm, delivery by 15 Nov and ₹48,000 with 50% advance, right?"*
4. **Recap:** a plain-language summary in English, Hindi or Kannada goes to the other party, who confirms with one tap.
5. **Receipt:** every message and every agreement version is hashed, chained and timestamped, and anyone can check it on an offline verify page.

Nobody is sent a "contract". They are sent a friendly confirmation, and the legal record builds itself.

---

## 3. What makes it special (speciality and uniqueness)

ChatGPT and Claude can already explain a chat or a notice once. Vachan is a different kind of product.

| Capability | General chatbot | Vachan |
| --- | --- | --- |
| Explains a chat when you paste it | Yes | Yes |
| Keeps a live structured record of agreed terms, each linked to its source message | No | **Yes** |
| Warns **during** the conversation what is missing | No | **Yes** |
| Suggests the next message that closes a legal gap | No | **Yes** |
| Two-party one-tap confirmation with versions (a changed deadline shows as a diff, not a new contract) | No | **Yes** |
| Tamper-evident evidence trail with a verify page that needs no login | No | **Yes** |
| Runs fully offline, so business chats never leave the device | No | **Yes** |
| Runs from a 16 GB pendrive on any laptop, nothing to install | No | **Yes** |

**Our three differentiators**

1. **Prevention, not explanation.** The system acts while the chat is happening, so the dispute never forms.
2. **Relationship-safe.** Friendly nudges and one-tap recaps replace awkward contracts.
3. **Private and provable.** Local AI keeps data on the stick, and the hash-chained receipt makes the record verifiable by a third party.

---

## 4. Features

### Core (must work in the demo)

| Feature | What it does |
| --- | --- |
| Chat ingestion | Parses WhatsApp "Export chat" text, plus a built-in two-party chat simulator |
| Term extraction | Fills a fixed schema: parties, scope, price, quantity, delivery date, payment terms, advance, penalty, GST status. Each field cites its source message |
| Gap detection | A checklist of required terms flags what is missing ("no payment due date mentioned") |
| Ambiguity and contradiction flags | Catches vague dates, approximate prices and conflicting values ("₹50k" earlier, "₹45k" later) |
| Evidence Strength score (0 to 100) | Shows how provable the deal is today: which terms are present, clear and acknowledged by both sides |
| Smart next message | Suggests a natural reply in Casual, Polite or Firm tone that closes the top gap |
| Plain-language recap | Short agreement in English, Hindi or Kannada for both sides to confirm |
| One-tap confirmation | Each party agrees through a link, and the confirmation is recorded |
| Tamper-evident receipt | Per-message hashes, a Merkle commitment, a chain of agreement versions, and a timestamp |
| Offline verify page | A static page that checks a receipt with no internet and no backend |

### Strong add-ons

- **Dispute-readiness view:** "If this went to the MSME Facilitation Council today, here is what you could prove and what you could not." This replaces risky verdict prediction.
- **Integrity red flags:** out-of-order timestamps, impossible gaps, format irregularities and contradictory terms. We call this *red flags*, not *fake detection*, because software cannot prove an export was authentic.
- **Voice-note support** through local speech-to-text.
- **Stamp-duty hint** for one or two states, with a link to e-stamping.
- **BSA s.63 certificate draft** adapted for chat evidence, unsigned and clearly labelled.

### Roadmap (say honestly that these are not built)

- WhatsApp Web extension for true live capture
- Blockchain anchoring when online
- LoRA fine-tuning on Indian informal-contract chats
- Mobile app

---

## 5. Wireframes

### Screen 1: Live deal workspace (the main screen)

```
+--------------------------------------------------------------------------+
|  VACHAN        Deal: Raju Traders x Meena Tailors      [Offline] [Eject] |
+---------------------------+----------------------------------------------+
|  CHAT                     |  LIVE ANALYSIS                               |
|                           |                                              |
|  Raju: 200 shirts, 480    |  Evidence Strength:   [#######---]  68 / 100 |
|        each ok?           |                                              |
|  Meena: ok. delivery      |  TERMS FOUND                                 |
|         next week         |  [x] Parties        Raju, Meena      (msg 1) |
|  Raju: advance half now   |  [x] Quantity       200 shirts       (msg 1) |
|  Meena: done sent 48000   |  [x] Price          Rs 480 each      (msg 1) |
|                           |  [!] Delivery       "next week"  AMBIGUOUS   |
|                           |  [ ] Final payment  MISSING                  |
|                           |  [ ] Penalty/late   MISSING                  |
|                           |                                              |
|                           |  SUGGESTED NEXT MESSAGE                      |
|                           |  "Just to confirm, delivery by 15 Nov and    |
|                           |   balance Rs 48,000 on delivery, right?"     |
|                           |  [Casual] [Polite] [Firm]     [Use this]     |
+---------------------------+----------------------------------------------+
|  [Type a message...]                                    [Send]           |
+--------------------------------------------------------------------------+
```

### Screen 2: Recap and one-tap confirmation

```
+---------------------------------------------------------------+
|  RECAP  (English | हिन्दी | ಕನ್ನಡ)                              |
|                                                               |
|  Hi Meena, just confirming what we discussed:                 |
|   - 200 shirts at Rs 480 each = Rs 96,000                     |
|   - Rs 48,000 advance received                                |
|   - Balance Rs 48,000 on delivery by 15 Nov                   |
|                                                               |
|  Each line links back to the original message  [view source]  |
|                                                               |
|  Raju: CONFIRMED          Meena: [ Tap to confirm ]           |
+---------------------------------------------------------------+
```

### Screen 3: Receipt and verify

```
+---------------------------------------------------------------+
|  RECEIPT                                                      |
|  Agreement version 2   (v1 -> v2 changed: delivery date)      |
|  Commitment hash:  9f3a...c71e                                |
|  Chain:  [Chat] -> [v1] -> [v2] -> [Confirmed]                |
|  Timestamp: 24 Oct 2026, 11:42                                |
|                                                               |
|  [Export bundle]  [Draft s.63 certificate]  [Open verify page]|
|                                                               |
|  VERIFY (works offline):  Result:  UNCHANGED since recording  |
|  Note: proves the record was not altered after upload, not    |
|  that the original export was genuine.                        |
+---------------------------------------------------------------+
```

---

## 6. System architecture

```
            USB PENDRIVE (16 GB, exFAT, encrypted vault)
+--------------------------------------------------------------------+
|  START.bat / start.sh  -> checks RAM -> picks 7B or 3B model       |
|                                                                    |
|   Browser UI  <--->  Local backend (localhost)                     |
|  (static web app)    |        |            |            |           |
|                      |        |            |            |           |
|               Chat parser   Local LLM    Whisper.cpp   Hash engine |
|               (WhatsApp)    (llama.cpp / (voice notes) (SHA-256,   |
|                             llamafile)                 Merkle,     |
|                             JSON-schema                version     |
|                             constrained                chain)      |
|                      |                                  |          |
|                      +------> SQLite (WAL) + evidence folder       |
|                                                                    |
|  verify.html  (static, offline, no backend call)                   |
+--------------------------------------------------------------------+
        No internet needed. Optional later: anchoring, WhatsApp Web.
```

**Key design rule:** the AI only *suggests*. It never touches the hash path, and a human confirms every term, so the evidence record stays trustworthy even if the model makes a mistake.

---

## 7. Tech stack and why we chose each part

| Layer | Choice | Why |
| --- | --- | --- |
| Local LLM | Qwen2.5 7B Q4 (3B fallback) via llama.cpp or llamafile | Runs on a normal laptop CPU, needs no installer or admin rights, and keeps data on the device |
| Structured output | JSON-schema constrained decoding | Forces valid, predictable fields so extraction is reliable |
| Speech to text | Whisper.cpp (base or small) | Offline voice-note transcription, including Hindi |
| Backend | Python FastAPI or Node, bundled | Small, fast to build, easy to run from a folder |
| Database | SQLite in WAL mode | A single file on the stick, no server to install, safe against abrupt removal |
| Frontend | Static HTML, JS and Tailwind, served on localhost | No build step at demo time, works in any browser |
| Integrity layer | SHA-256, Merkle tree, per-version hash chain | Reused from our earlier DigiVault design, proven and explainable |
| Verify page | Static `verify.html` | A third party can check a receipt with no account and no backend call |
| Security | Passphrase-encrypted vault (AES-GCM) | The stick can be lost, so the data must be protected |
| Launcher | `START.bat` plus `start.sh` | One double-click, relative paths only |
| Format | exFAT | FAT32 cannot hold files over 4 GB |

---

## 8. Why we chose this problem (LS-06)

We compared all six Legal Services statements.

| Problem | Why we did or did not choose it |
| --- | --- |
| LS-05 Notice triage | Most crowded pick, and general chatbots already explain a notice well. Weak differentiation |
| LS-01, LS-02, LS-04 | Serve owners who are already trying to comply, and results are hard to show in a short demo |
| LS-03 MSME payments | Strong, but narrower, and it depends on having provable terms in the first place |
| **LS-06 Informal agreements** | **Root-cause problem: provable terms are what every other legal right depends on. Wide audience, a real demo, and a clear technical edge** |

**Our reasoning:** if a deal is not recorded clearly, no later right (payment, delivery, dispute resolution) can be enforced. LS-06 sits upstream of LS-03 and LS-05, so solving it prevents many of those problems from starting.

---

## 9. Why local and portable

- **Privacy:** business chats hold prices, customer names and bank details. Nothing leaves the device.
- **Accessibility:** no cloud account, no subscription, works in places with poor connectivity.
- **Trust:** the user can see that data stays on their own stick.
- **Demo proof:** pull the Wi-Fi, plug in the pendrive, double-click, and run the full flow offline.

---

## 10. Responsible AI and honest limits

Saying these ourselves, before judges ask, builds trust.

- **Drafting aid, not legal advice.** The tool organises and explains. It does not replace a lawyer.
- **No verdict prediction.** We show evidence strength and dispute-readiness instead, because predicting a court outcome cannot be validated.
- **Tamper evidence is not authenticity.** We can prove a record was unchanged after upload. We cannot prove the original chat export was genuine. The product says so on screen.
- **Human in the loop.** Every extracted term links to its source and needs user confirmation.
- **Small-model limits.** Local models are weaker on Hinglish and Kannada-English, so we report measured accuracy on our test chats rather than claims.
- **Stamp duty varies by state.** We cover a small number of states and mark figures as needing verification.

---

## 11. Demo script (about 4 minutes)

1. **Problem (30 s):** show a messy real-style chat with a vague deadline and no payment term.
2. **Offline proof (20 s):** disconnect Wi-Fi, plug in the pendrive, double-click START.
3. **Live analysis (60 s):** play the chat, watch terms appear with sources, see the ambiguity flag and a score of 68.
4. **Next message (30 s):** accept the suggested reply, and watch the score rise to 90.
5. **Recap and confirm (45 s):** generate the Kannada or Hindi recap, and the other party taps to confirm.
6. **Receipt and tamper test (45 s):** change one character in the exported chat, and the verify page flags it.
7. **Close (10 s):** *"Others explain the dispute after it happens. We help you avoid it while you are still chatting."*

Prepare three sample chats: clean, ambiguous and contradictory. Keep a recorded backup video.

---

## 12. Likely judge questions and answers

**Why not just use ChatGPT?** It explains once and forgets. We keep a live structured record, warn during the chat, suggest the next message, collect confirmation from both sides, and produce a verifiable receipt, all offline.

**Is this legal advice?** No. It is a drafting and record-keeping aid, and it says so. Oral and chat agreements can already be valid contracts, and our goal is to make them provable.

**Can it detect fake chats?** Not with certainty, and we do not claim that. We flag integrity red flags such as timestamp problems and contradictions, and we prove tamper evidence from the moment of upload.

**Did you train your own model?** We run an open model locally with schema-constrained output. Fine-tuning is on the roadmap, and we only claim it if it is done.

**Does it work in Indian languages?** English, Hindi and Kannada recaps are supported, and we show measured accuracy on Hinglish and Kannada-English samples.

**What if the pendrive is lost?** The vault is passphrase-encrypted, so the data is unreadable without the passphrase.

**Who is it for?** Freelancers, shopkeepers, tutors, contractors, landlords and small suppliers, anyone who makes deals over chat.

**How will it scale or make money?** A free offline version for individuals, then a paid team version with sync, WhatsApp integration and a CA or lawyer review marketplace.

---

## 13. Impact summary

- **Who benefits:** the millions of small operators who deal informally and cannot afford disputes.
- **What changes:** deals become provable without anyone feeling like they are signing a contract.
- **Why it lasts:** privacy-first, offline-capable, and built on a verifiable record that courts and counterparties can check themselves.

**Closing line:** *Handshake → Recap → Receipt. A promise made in chat should be a promise you can prove.*
