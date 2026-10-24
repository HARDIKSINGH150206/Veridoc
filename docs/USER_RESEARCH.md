# User Research

This file holds the interview template and notes format for talking to small operators (tailors, printers, freelancers, tutors, contractors, caterers, photographers, informal lenders) and to people who check records (lawyers, CAs, council staff). Interviews check the assumptions in the PRD. No findings are recorded yet. Interviewers are `TBD`. Never include real names, phone numbers or chat contents in this file.

Last updated: 2026-10-25
Status: Draft v1

## 1. Goals

1. Check how people agree deals today (chat, voice, in person).
2. Check whether gaps like "next week" cause real problems for them.
3. Test whether the counterparty would reply with a short code.
4. Test the recap wording in English and Hindi.
5. Learn what a verifier (lawyer, CA) needs from a record.
6. Learn what would make the tool feel legalistic.

## 2. Ethics and consent

1. Tell the person who you are, why you are asking, and that taking part is voluntary.
2. Ask before taking notes or recording. If they decline, take notes by hand.
3. Do not ask for real chats. If they volunteer, do not copy them into the repository; describe the pattern instead.
4. Store notes without names. Use a code like `P-03`.
5. Share only anonymised summaries in the team chat.
6. Offer to share what you learn.
7. Anything they say about law is their view, not a legal fact. A lawyer must confirm (OPEN_QUESTIONS Q-02).

## 3. Participant tracker

| Code | Role | Language | City or region | Date | Interviewer | Consent recorded |
|---|---|---|---|---|---|---|
| P-01 | TBD | TBD | TBD | TBD | TBD | TBD |

Target mix (to be decided, Q-42): about 10 small operators across at least 4 trades, 2 to 3 lawyers or CAs, and 1 to 2 people from a council or similar body.

## 4. Interview template for small operators (about 30 minutes)

**Warm-up (3 min)**
1. What do you do? How many customers or suppliers do you deal with in a month?
2. Which language do you use with them? Which app?

**How deals are agreed (7 min)**
3. Think of your last deal. How did it begin? How did you agree price and delivery?
4. Do you use voice notes? For what?
5. Did anything get misunderstood? What happened?
6. Has anyone paid late or refused to pay? What did you do? What did you wish you had written down?

**Records (5 min)**
7. Where do you keep records of deals? Could you find the message from three months ago?
8. Have you ever shown a chat to anyone (lawyer, officer, bank)? What happened?

**Reaction to the idea (8 min)** (describe in one minute; do not demo yet)
9. If a tool noticed that "next week" had no date and suggested a message to ask, would you send it? What would you change in the wording?
10. If your customer received a short summary and had to reply `CONFIRM 7F3K`, would they do it? What would put them off?
11. Show the English and Hindi recap. Is every line clear? Which words are strange?
12. Does a record like this feel like a contract? Does that feel awkward?

**Trust and privacy (4 min)**
13. Would you be comfortable with a tool that reads your customer chats on your own laptop? What would worry you?
14. Who would you show the record to?

**Close (3 min)**
15. What is the one thing that would make you use this? What would stop you?
16. May we contact you again for testing?

## 5. Interview template for verifiers (lawyer, CA, officer; about 30 minutes)

1. What do you receive as evidence in informal deals? What do you ask for?
2. What makes a chat record useful or useless to you?
3. Show the dispute pack and the verify page. What is missing? What is confusing?
4. How do you read "the record was not changed after it was saved"? What would you want it to say instead?
5. What do you need on the Section 63 certificate draft? Who must sign? (Note their view; a lawyer must confirm.)
6. What would you never rely on?

## 6. Notes format

One file per interview in `docs/research/` (create the folder when the first interview is done), named by code, for example `P-03.md`:

```
Code: P-03
Role / trade:
Language:
Date and interviewer:
Consent: yes/no (recording yes/no)

Summary (3 lines):

Quotes (anonymised, exact words, with the language):

Pain points:

Current behaviour:

Reaction to: suggested message / echo code / recap / verify page

Wording they suggested:

Surprises:

Follow-ups:
```

## 7. Synthesis

After each batch of 3 to 5 interviews, write one page: what repeated, what surprised us, which PRD assumption changed. Open a pull request that links to the affected requirement IDs. Findings that change scope go through the normal PRD change process.

## 8. Assumptions to test

| # | Assumption (from PRD section 18) | Evidence needed |
|---|---|---|
| 1 | Users export chats themselves | How many can export a chat? What goes wrong? |
| 2 | The counterparty will reply with a short code | Yes or no, and what wording works |
| 3 | A short recap in Hindi is clear | Reading test results |
| 4 | Verifiers accept the tamper-evident wording | Their feedback on the limit text |
