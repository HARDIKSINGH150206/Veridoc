# Demo Day Runbook

This runbook is the plan for the day of the demo: the timeline, who does what, the equipment list, the checks to run, and what to do when something fails. The demo itself is scripted in [DEMO_SCRIPT](DEMO_SCRIPT.md) and the fallback plan is there too; this file covers the surrounding day. Names, times and the venue are `TBD` (OPEN_QUESTIONS Q-10).

Last updated: 2026-10-25
Status: Draft v1

## 1. Roles

| Role | Person | Duty |
|---|---|---|
| Presenter (acts as Raju) | TBD | Speaks and drives the demo laptop |
| Second person (acts as Meena) | TBD | Replies on the phone; answers judge questions on the AI |
| Operator | TBD | Backup laptop, recorded video, timer, networking |
| Q&A lead | TBD | Answers legal and integrity questions using [JUDGE_QA](JUDGE_QA.md) |

## 2. Timeline

All times are `TBD` and set once the event schedule is known.

| When | What |
|---|---|
| Two days before | Build the demo stick from the tagged `v0.4-phase4` commit; run the full RELEASE_CHECKLIST |
| Day before | Final rehearsal on the demo laptop and the backup laptop; charge everything; print the recovery key and the one-page cheat sheet |
| Morning | Pack the equipment list; test the stick on the demo laptop once more |
| Arrival | Find the power, the table and the screen; set up the laptops; do the pre-flight checks (section 4) |
| 30 minutes before slot | Close all other apps; do the pre-flight again; open the tabs |
| Slot | Run the four-minute script |
| After | Q&A; collect feedback; note questions in OPEN_QUESTIONS |

## 3. Equipment list

- [ ] Demo laptop (not a development machine) with charger
- [ ] Backup laptop with the same build and charger
- [ ] Two USB 3 sticks (exFAT) with the same tagged build, and one spare
- [ ] Phone with WhatsApp and a prepared chat, and the second person's phone
- [ ] A second phone with the recorded backup video, and the video on both laptops
- [ ] Printed recovery key and passphrase card (kept apart from the sticks)
- [ ] HDMI, USB-C and display adapters; extension lead
- [ ] A phone hotspot (not used by the app; for chat messages on the phone only)
- [ ] The tampered receipt bundle prepared for the backup tamper test
- [ ] Printed one-page cheat sheet: script timings and the limits wording
- [ ] Water and a charger for the phones

## 4. Pre-flight checklist (run on each laptop)

- [ ] Battery above 80% and plugged in; power saving off; notifications off
- [ ] Wi-Fi off (the demo proves offline); Bluetooth off
- [ ] Stick plugged in; the launcher starts the app
- [ ] The UI is usable in under 15 seconds from the stick (target; note the actual time)
- [ ] The vault unlocks with the passphrase
- [ ] The model hash check shows "Hash verified" in settings (or safe mode is deliberately on)
- [ ] Samples load: clean, ambiguous, contradictory, voice
- [ ] Play the moment plays the voice clip
- [ ] The Hindi recap shows Devanagari correctly
- [ ] The WhatsApp phone can receive the recap text and send `CONFIRM <code>`
- [ ] The verify page opens by double-click and the tamper test turns UNCHANGED into ALTERED
- [ ] The recorded video plays on the demo laptop and on the phone
- [ ] Screen scaling and font sizes are readable from the back of the room

## 5. If something fails

The full table is in [DEMO_SCRIPT](DEMO_SCRIPT.md) section 5. The short rules:
1. Do not apologise at length. Say what happened in one sentence and switch.
2. Keep the time: the operator signals at 2:00 and 3:00.
3. AI slow: carry on with rules results and say the AI refines in the background.
4. Phone fails: paste the prepared reply text.
5. Stick or antivirus problem: switch to the backup laptop, then to the video.
6. Total failure: play the recorded video and narrate it. Never improvise a claim.
7. Do not quote a number that is not in the trust report. If asked for one, say it is a target until measured.

## 6. After the demo

- [ ] Write down every judge question and who answered it
- [ ] Add new questions to JUDGE_QA and any open item to OPEN_QUESTIONS
- [ ] Back up the demo stick image
- [ ] Short team retro: what to keep, what to change
