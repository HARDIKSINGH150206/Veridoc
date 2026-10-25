// Test helper for the end-to-end test: runs the screen's own logic on JSON read from stdin.
// Input: { terms, messages, participants, at }. Output: the confirmable terms as AgreedTerms
// and the source labels of every term, exactly as the screen would build them.
import { readFileSync } from 'node:fs';

import { canConfirm, describeValue, primaryUser, sourceLabels, statusView, toAgreedTerm } from '../screens/skeleton/logic.js';

const input = JSON.parse(readFileSync(0, 'utf8'));
const me = primaryUser(input.participants);
const view = input.terms.map((term) => ({
  key: term.key,
  status: statusView(term.state),
  value: describeValue(term.value),
  sources: sourceLabels(term, input.messages),
  confirmable: canConfirm(term),
}));
const agreed = input.terms.filter(canConfirm).map((term) => toAgreedTerm(term, me, input.at));
process.stdout.write(JSON.stringify({ view, agreed }));
