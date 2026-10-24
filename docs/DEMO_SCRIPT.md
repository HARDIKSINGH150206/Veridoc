# Demo Script

This is the four-minute live demo, the sample chats it needs, the fallback plan and the recorded backup. It follows the flow Handshake, Recap, Receipt. Timings are plans, not measurements.

Last updated: 2026-10-25
Status: Draft v1

## 1. Roles and setup

| Role | Person |
|---|---|
| Presenter (acts as Raju) | TBD |
| Second person (acts as Meena, answers on a phone) | TBD |
| Operator (backup laptop, video) | TBD |

Setup checklist:
1. The USB 3 stick holds the release build. A second laptop (not a development machine) is used for the demo.
2. A phone with WhatsApp holds a prepared chat, so the recap can be shown arriving and "CONFIRM <code>" can be sent. If the phone fails, use the sample reply text.
3. The vault already has a passphrase set. The recovery key is printed and kept aside.
4. Wi-Fi is on at the start, to be turned off on stage.
5. Samples loaded: clean, ambiguous, contradictory, and one with a voice note.
6. Hindi fonts verified on the demo laptop.
7. A tampered copy of the receipt bundle is prepared in advance as a backup for the tamper test.

## 2. Sample chats needed

| Sample | Purpose | Content summary |
|---|---|---|
| Clean | Shows a high score and no flags | Raju and Meena (or another pair) agree on every term with fixed dates and amounts |
| Ambiguous (main demo) | Shows flags and a suggestion | 200 shirts, ₹480 each, ₹48,000 advance, "delivery next week", no final payment, no late penalty |
| Contradictory | Shows the Conflict flag | Price ₹50,000 in one message and ₹45,000 in another |
| Voice sample | Shows text versus voice contradiction and play the moment | Text says 15 Nov; a voice note says 22 Nov |
| Hinglish sample | Shows rules for number words | Includes "pachaas hazaar" and "aadha advance" |

All samples are synthetic. Each has a gold label file in `eval/labels/` (Area 2) and the chat file is provided by Area 1.

## 3. The four-minute script

| Time | Step | What to do and say | Screen |
|---|---|---|---|
| 0:00 to 0:25 | Problem | Show the ambiguous chat in WhatsApp. "A real deal: price in one message, delivery 'next week', balance never mentioned. This is how most small deals work." | Phone, then S2 |
| 0:25 to 0:40 | Offline proof | Turn Wi-Fi off. Plug in the stick, double-click START. "Everything runs on this laptop." Point to the Offline mode indicator. | S1 |
| 0:40 to 1:30 | Live analysis | Load the ambiguous sample. Terms appear with sources. Open delivery in S4: the reason "next week could be 5 to 12 days away". Show the voice note: text says 15 Nov, voice says 22 Nov, press Play the moment. Show the score. | S2, S3, S4 |
| 1:30 to 1:55 | Next message | Show the suggested message, switch tone, press Use this. Import the reply (or add it in the simulator). The score rises. "Others explain the dispute after it happens. We help you avoid it while you are still chatting." | S3 |
| 1:55 to 2:20 | Blind Handshake (first to drop) | Both answer four questions privately, seal, reveal. Show a delivery date mismatch. If time is short, skip it. | S5 |
| 2:20 to 3:00 | Recap and confirm | Generate the Hindi recap. Copy the WhatsApp message with the code. The second person replies "CONFIRM <code>" on the phone. Paste the reply. Show Confirmed. | S6, S12 |
| 3:00 to 3:50 | Receipt and tamper test | Open the receipt: chain, root, device-clock time. Open the verify page: UNCHANGED with each check. Change one character in the exported chat. Verify again: ALTERED, naming message #7. Read the limit line aloud. | S8, S9 |
| 3:50 to 4:00 | Close | "Handshake, Recap, Receipt. A promise made in chat should be a promise you can prove." | S1 |

The dispute pack (S10) is mentioned in one sentence ("one export for a lawyer or the MSME Facilitation Council") and shown only if time allows.

## 4. Success criteria

**Numbers on screen.** Every score and metric shown in the demo comes from the real formula (PRD FR-SCO-001) or from a named trust report. The values in the wireframes (for example 68) are illustrative only and must not be spoken as results. Rehearse with the actual computed score for the chosen sample.


See PRD section 15. In short: runs offline on a second laptop; flags shown; score rises; Hindi recap confirmed; tamper test names the changed message; within about four minutes.

## 5. Fallback plan

| Failure | Fallback |
|---|---|
| AI model slow or failing | Keep going: rules results appear first. Switch safe mode on if needed. Say so. |
| Voice transcription slow | Use the pre-imported voice sample; transcription runs at import, not live |
| Stick not recognised or antivirus blocks | Use the laptop install of the same build, or the recorded video |
| Phone or WhatsApp fails | Paste the prepared reply text "CONFIRM <code>" from the second laptop notes |
| Wrong code or recap changed | Show the "not confirmed" state, then regenerate; it is also a good demo of stale codes |
| Hindi font problem | Switch the recap to English |
| Verify page fails to open | Use the pre-opened tab on the backup laptop |
| Total failure | Play the recorded backup and narrate |

## 6. Recorded backup

1. Record the full flow on the demo laptop with the network off, with voice-over, within four minutes.
2. Record a second short clip of the tamper test alone.
3. Keep both on the stick, on the laptop and on a phone. Name the files with the build commit.
4. Re-record if the UI changes.
5. Narration text matches this script and uses only measured numbers from a named trust report.

## 7. Questions to expect

See [JUDGE_QA](JUDGE_QA.md).
