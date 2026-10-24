# Judge Q&A

Likely questions from judges with short, honest answers. Numbers are quoted only from a trust report that was actually run; until then they are targets.

Last updated: 2026-10-25
Status: Draft v1

## Product and problem

**Why not just use ChatGPT or Claude?**
A chatbot explains a chat once. VeriDoc keeps a live structured record where each term links to its source message or voice-note time range. It warns during the chat, suggests the next message, collects confirmation from both sides, and produces a record anyone can check. It also runs offline, so business chats stay on the device.

**Who is it for?**
Small suppliers and vendors who deal over chat: tailors, printers, freelancers, tutors, contractors, caterers, photographers, and people who lend money informally.

**Why LS-06?**
Provable terms come before every other right. If a deal is not recorded clearly, payment, delivery and dispute rights are hard to enforce later. LS-06 sits upstream of the MSME payment and notice problems.

**What does it do that is not just a template generator?**
It does not start from a template. It starts from what the parties actually said, shows what is missing, and builds the recap from confirmed terms.

## Legal

**Is this legal advice?**
No. It is a drafting and record-keeping aid, and it says so on screen. A lawyer must confirm every statement about Indian law.

**Is a chat agreement valid?**
Some agreements made over chat may be valid contracts. We do not decide that; we make the terms and the evidence clearer. Confirm with a lawyer.

**Do you replace a registered or stamped agreement?**
No. Some deals may need a written, stamped or registered document. The playbook tells the user to ask a lawyer.

**What is the Section 63 certificate?**
An unsigned draft certificate for electronic records, included in the dispute pack. The person responsible for the device must complete it. A lawyer must confirm its form and use.

**Will this stand up in court?**
We make no promise. The dispute pack is a court-ready evidence package in the sense of an organised export with a timeline, hashes and a verification guide. Admissibility is for the court.

## Integrity

**What does the hash prove?**
That the record was not changed after it was saved. It does not prove the original chat export was genuine. The product says this on the receipt and verify screens.

**Can it detect fake chats?**
No, and we do not claim it. In P1 it flags integrity red flags such as timestamp order problems; these are warnings, not verdicts.

**What if the device clock is wrong?**
Then the recorded time is wrong. S8 says the time comes from the device. Optional anchoring (P1) gives an independent time.

**Why a salted Merkle tree?**
Salts stop guessing of hidden messages. The tree lets us share only chosen messages later and still verify them against the same root.

**Can the other person fake the confirmation?**
The code is a short binding check on the exact recap, not authentication. The reply is stored as evidence and must come from the counterparty in the chat. It relies on the export being genuine, and we say that.

**Can the record be made impossible to change?**
No. It is tamper-evident: a change after saving is detected, not prevented.

## AI

**Which model do you use? Did you train it?**
We run small open models locally with schema-constrained output. Exact models are chosen after benchmarks (TBD). We do not train or fine-tune and make no claim of it.

**What if the AI is wrong?**
The AI only suggests. Every value must appear in a real message or transcript span. If rules and AI disagree, the term is marked needs review. A person confirms every term. Without the model, safe mode runs rules only.

**What about prompt injection in a chat?**
Chat text is treated as data. Output is schema-constrained, values are grounded, and injection tests are part of the eval.

**How accurate is it?**
Our target is at least 90% field-level extraction on our eval set of about 100 chats. The measured number comes from the trust report; we show it by language, including Hinglish and Kannada-English where small models are weaker. Until a report is run, this is a target.

**Does it work in Indian languages?**
English and Hindi recaps in the MVP. Kannada is P1 after native-speaker review. Extraction is tested on Hinglish and Kannada-English chats and Hindi voice notes.

**Does the AI send messages for me?**
No. It suggests; you copy and send it yourself.

## Privacy and security

**Does data leave my laptop?**
Not by default. There is no cloud AI. Optional anchoring sends only a hash. The optional share link sends only ciphertext.

**What about the other person's privacy?**
We process their messages on your device. A lawyer must review data-protection duties (DPDP) before public launch. This is an open item.

**What if the stick is lost?**
The vault is encrypted with a key derived from your passphrase. A recovery key is printed at setup. If both are lost, the data cannot be opened.

## Business and scope

**How will it make money?**
Hypothesis, not validated: free offline individual version, then a paid team tier with sync and optional professional review. See ROADMAP.

**Is the pendrive the product?**
No. It is a delivery vehicle and demo proof. The same build installs on a laptop.

**What did you build for this event?**
All code is new. DigiVault informed the integrity design only. See PRIOR_WORK.

**What is not built?**
Android app, phone web app, in-person voice sealing, UPI screenshot check, CA countersign, cloud sync, teams and billing, WhatsApp extension. P1 items are listed in the roadmap.

**What did you cut and why?**
Reliability scores, fake-chat detection claims, verdict prediction, a template library, a payment ledger, an interest calculator, notice escalation, fine-tuning claims and RAG. They cannot be validated, drift into legal practice, or are outside LS-06.

**Will the other party really reply with a code?**
It is one short WhatsApp reply to a friendly message, with no link and no install. The confirmation rate is a metric we will measure in a pilot; we have no number yet.
