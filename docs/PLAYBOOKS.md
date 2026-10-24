# Playbooks

A playbook tells the deal-agnostic engine what a given kind of deal needs: which terms are required and how much each is worth, which wordings are ambiguous, which legal hints apply, which questions the Blind Handshake asks, and which fixed templates produce recaps and suggestions. This document defines the format and writes out the two MVP playbooks in full.

Last updated: 2026-10-25
Status: Draft v1

All Hindi text below is a draft and needs native-speaker review before the demo (see [OPEN_QUESTIONS](OPEN_QUESTIONS.md)). Legal hints are conservative and a lawyer must confirm them.

## 1. Format

One YAML file per playbook in `playbooks/` (Area 2). Templates live in `playbooks/templates/<lang>/` (Area 1, who builds recaps and handshake messages from them). The engine validates a playbook at startup and refuses invalid files with the line number.

```yaml
key: string                     # unique, snake_case
version: integer
title: {en: string, hi: string}
terms:                          # ordered list
  - key: string                 # unique within the playbook
    label: {en: string, hi: string}
    required: boolean
    weight: integer             # weights of required terms sum to 100
    type: party|text|quantity|money|date|percent|duration|enum
    ask_order: integer          # lower is asked first on a tie
    parsers: [string]           # names of rules parsers to run
    ambiguity: [string]         # names of ambiguity rules that apply
    pairs_with: [term_key]      # may be asked in the same message
ambiguity_rules:
  - id: string
    type: AMBIGUOUS_DATE|AMBIGUOUS_AMOUNT|VAGUE_QUANTITY|VAGUE_PAYMENT
    patterns: [string]          # regex or word lists, per language
    reason: {en: string, hi: string}
legal_hints:
  - id: string
    when: {keywords: [string]}  # matched against confirmed terms and messages
    text: {en: string, hi: string}
handshake_questions: [term_key] # 3 to 4 keys
recap:
  template_set: string          # folder name under templates/
suggestions:
  template_set: string
```

Rules:
1. Weights of required terms sum to 100.
2. A term with `required: false` is shown and recapped if present, but does not affect the score or raise MISSING_TERM.
3. Every user-facing string has English and Hindi (Kannada added in P1).
4. A playbook contains no code. Parser and rule names refer to code registered in `packages/intelligence`.
5. Adding a playbook needs no engine change.

## 2. Playbook: supply or order (`supply_order.yaml`)

For goods and made-to-order work: cloth, shirts, banners, catering, printing, materials.

### Terms

| Key | Label | Required | Weight | Type | Ask order | Pairs with |
|---|---|---|---|---|---|---|
| parties | Parties | yes | 10 | party | 8 | |
| scope | What is being supplied | yes | 10 | text | 7 | quantity |
| quantity | Quantity | yes | 10 | quantity | 6 | scope |
| price | Price | yes | 15 | money | 3 | |
| advance | Advance paid or due | yes | 10 | money | 5 | final_payment |
| delivery_date | Delivery date | yes | 15 | date | 1 | final_payment |
| final_payment | Balance and when it is due | yes | 15 | money | 2 | delivery_date, advance |
| late_penalty | What happens if late | yes | 15 | text | 4 | delivery_date |
| gst_status | GST on the price (included, extra, not applicable) | no | 0 | enum | 9 | price |

Required weights: 10 + 10 + 10 + 15 + 10 + 15 + 15 + 15 = 100.

### Ambiguity rules

| ID | Type | Examples that trigger it | Reason shown (English) |
|---|---|---|---|
| rel_date | AMBIGUOUS_DATE | next week, this month, soon, kal, parso, jaldi | "A relative date with no fixed day. 'Next week' could be 5 to 12 days away depending on the reader." |
| partial_date | AMBIGUOUS_DATE | "15th" with no month, "15 Nov" with no year across a year boundary | "The date is missing its month or year." |
| order_date | AMBIGUOUS_DATE | 03/04/2026 where day-first and month-first both parse | "This date can be read two ways: 3 April or 4 March." |
| approx_amount | AMBIGUOUS_AMOUNT | approx, around, about, lagbhag, 40 to 50k | "This is an approximate or ranged price, not a fixed one." |
| vague_qty | VAGUE_QUANTITY | some, a few, as needed, zarurat ke hisaab se | "The quantity is not a number." |
| vague_pay | VAGUE_PAYMENT | will pay soon, later, baad mein, when I can | "'Soon' does not give a payment date." |
| half_adv | VAGUE_PAYMENT | "half advance" with no total price | "Half of what? The total price is not fixed yet." |

### Legal hints

| ID | When | Text (English) |
|---|---|---|
| property_hint | Keywords such as plot, flat, land, property, zameen, makaan, lease | "A deal about property or a long lease may need a written and registered document. VeriDoc does not replace one. Please ask a lawyer." |
| value_hint | None (shown in About) | "Some agreements may need to be written or stamped to be enforced. A lawyer can tell you if yours does." |
| gst_note | `gst_status` not found | "GST is not mentioned. Ask your CA if it applies." |

All hints: confirm with a lawyer before they ship.

### Handshake questions

`delivery_date`, `final_payment`, `late_penalty`, `price` (four questions). If the user prefers three, `price` is dropped.

### Recap templates (English)

`playbooks/templates/en/supply_order.recap.yaml`. Fields in `{braces}`.

| Term key | Line template |
|---|---|
| greeting | `Hi {other_name}, just confirming what we discussed:` |
| scope + quantity + price | `{quantity} {scope} at {unit_price} each = {total}` |
| advance | `{advance} advance {advance_state}` where `advance_state` is `received` or `due on {advance_date}` |
| delivery_date | `Delivery by {delivery_date}` |
| final_payment | `Balance {balance} {balance_when}` where `balance_when` is `on delivery`, `within {n} days of delivery`, or `on {date}` |
| late_penalty | `If delivery is late: {penalty_text}` |
| gst_status | `GST: {gst_text}` |
| closing | `If all correct, reply: CONFIRM {code}` |

Example output (matches S12):

```
Hi Meena, just confirming what we discussed:
• 200 shirts at ₹480 = ₹96,000
• ₹48,000 advance received
• Delivery by 15 Nov
• Balance ₹48,000 on delivery
If all correct, reply: CONFIRM 7F3K
```

### Recap templates (Hindi, draft)

| Term key | Line template |
|---|---|
| greeting | `नमस्ते {other_name}, हमारी बात का सार यह है:` |
| scope + quantity + price | `{quantity} {scope}, ₹{unit_price} प्रति नग = ₹{total}` |
| advance | `₹{advance} एडवांस {advance_state}` (`मिल गया` or `{advance_date} तक देना है`) |
| delivery_date | `डिलीवरी {delivery_date} तक` |
| final_payment | `बाकी ₹{balance} {balance_when}` (`डिलीवरी पर`, `डिलीवरी के {n} दिन के अंदर`, `{date} को`) |
| late_penalty | `देरी होने पर: {penalty_text}` |
| closing | `अगर सब सही है तो जवाब दें: CONFIRM {code}` |

The word `CONFIRM` and the code stay in Latin letters so the reply check is simple.

### Suggestion templates (English, gap: delivery_date + final_payment)

| Tone | Text |
|---|---|
| Casual | `Quick one: delivery by {delivery_date} and the balance {balance} on delivery, right?` |
| Polite | `Just to confirm, delivery by {delivery_date} and the balance {balance} on delivery, right?` |
| Firm | `To keep things clear, please confirm: delivery by {delivery_date}, balance {balance} due {balance_when}.` |

Other gaps have a template set per tone: `late_penalty`, `price` (conflict), `advance`, `quantity`, `scope`. Written in `playbooks/templates/en/supply_order.suggest.yaml` (Area 2). Firm tone is courteous and never threatens.

### Suggestion templates (Hindi, draft, gap: delivery_date + final_payment)

| Tone | Text |
|---|---|
| Casual | `एक बात पक्की कर लें: डिलीवरी {delivery_date} तक और बाकी {balance} डिलीवरी पर, ठीक है न?` |
| Polite | `बस पुष्टि के लिए: डिलीवरी {delivery_date} तक और बाकी {balance} डिलीवरी पर, सही है न?` |
| Firm | `बात साफ़ रहे इसलिए कृपया पुष्टि करें: डिलीवरी {delivery_date} तक, बाकी {balance} {balance_when}।` |

## 3. Playbook: freelance or service (`freelance.yaml`)

For design, writing, tutoring, photography, repairs, contracting and similar paid work.

### Terms

| Key | Label | Required | Weight | Type | Ask order | Pairs with |
|---|---|---|---|---|---|---|
| parties | Parties | yes | 10 | party | 8 | |
| deliverable | What will be delivered | yes | 20 | text | 1 | deadline |
| price | Fee | yes | 15 | money | 3 | payment_schedule |
| payment_schedule | When payments are due (advance, milestones, final) | yes | 15 | text | 2 | price |
| deadline | Deadline | yes | 15 | date | 4 | deliverable |
| revisions | Number of revisions or changes included | yes | 10 | quantity | 5 | |
| ownership | Who owns or may use the finished work | yes | 5 | enum | 7 | |
| cancellation | What happens if the work is cancelled or stopped | yes | 10 | text | 6 | |

Required weights: 10 + 20 + 15 + 15 + 15 + 10 + 5 + 10 = 100.

### Ambiguity rules

| ID | Type | Examples | Reason (English) |
|---|---|---|---|
| rel_date | AMBIGUOUS_DATE | by next week, ASAP, jaldi, end of month | "No fixed deadline day." |
| vague_scope | VAGUE_QUANTITY | a logo, some changes, basic website | "The deliverable is not specific enough to check later." |
| unlimited_rev | VAGUE_QUANTITY | until you are happy, any changes | "Unlimited changes are not a number." |
| approx_amount | AMBIGUOUS_AMOUNT | around 10k, 8 to 10k | "The fee is approximate or a range." |
| vague_pay | VAGUE_PAYMENT | after the work, when the client pays | "No payment date." |

### Legal hints

| ID | When | Text (English) |
|---|---|---|
| ip_hint | `ownership` not found, or keywords such as copyright, rights, licence | "Who owns the finished work may need to be in writing. Please ask a lawyer." |
| property_hint | Keywords for property or construction on land | "Work on property may need a written and registered document. Please ask a lawyer." |

All hints: confirm with a lawyer.

### Handshake questions

`deadline`, `payment_schedule`, `revisions`, `price`.

### Recap templates (English)

| Term key | Line template |
|---|---|
| greeting | `Hi {other_name}, just confirming what we discussed:` |
| deliverable | `Work: {deliverable}` |
| price | `Fee: {price}` |
| payment_schedule | `Payments: {payment_schedule}` |
| deadline | `Deadline: {deadline}` |
| revisions | `Changes included: {revisions}` |
| ownership | `Who may use the finished work: {ownership}` |
| cancellation | `If the work is stopped: {cancellation}` |
| closing | `If all correct, reply: CONFIRM {code}` |

### Recap templates (Hindi, draft)

| Term key | Line template |
|---|---|
| greeting | `नमस्ते {other_name}, हमारी बात का सार यह है:` |
| deliverable | `काम: {deliverable}` |
| price | `फ़ीस: {price}` |
| payment_schedule | `भुगतान: {payment_schedule}` |
| deadline | `समय-सीमा: {deadline}` |
| revisions | `शामिल बदलाव: {revisions}` |
| ownership | `तैयार काम का उपयोग कौन कर सकता है: {ownership}` |
| cancellation | `काम रुकने पर: {cancellation}` |
| closing | `अगर सब सही है तो जवाब दें: CONFIRM {code}` |

### Suggestion templates (English, gap: deadline + deliverable)

| Tone | Text |
|---|---|
| Casual | `Just so we are on the same page: {deliverable}, ready by {deadline}, right?` |
| Polite | `To confirm, you will receive {deliverable} by {deadline}. Does that work for you?` |
| Firm | `For clarity, please confirm the deliverable ({deliverable}) and the deadline ({deadline}).` |

## 4. Engine behaviour driven by playbooks

| Engine step | Playbook input |
|---|---|
| Extraction schema | `terms` |
| Missing-term flags | `required` terms with no accepted value |
| Ambiguity flags | `ambiguity_rules` |
| Score | `weight` of required terms |
| Suggestion ranking | `weight`, `ask_order`, `pairs_with` |
| Handshake | `handshake_questions` |
| Recap and suggestion text | `templates/<lang>/<set>` |
| Hints | `legal_hints` |

## 5. Adding a playbook

1. Copy an existing YAML and change `key`, `terms`, rules and hints.
2. Add template files for English and Hindi.
3. Add at least five labelled chats to `eval/` for the new playbook.
4. Run the trust report; do not ship below the accuracy target without noting it.
5. Have a lawyer review the legal hints.
