// Logic of the walking-skeleton screen (apps/web/screens/skeleton/logic.js). No DOM, no network.
import assert from 'node:assert/strict';
import { test } from 'node:test';

import * as logic from '../screens/skeleton/logic.js';

const ME = '11111111-1111-4111-8111-111111111111';
const M1 = '22222222-2222-4222-8222-222222222222';
const M2 = '33333333-3333-4333-8333-333333333333';
const messages = [{ id: M1, seq: 1 }, { id: M2, seq: 2 }];

const term = (over = {}) => ({
  key: 'unit_price',
  state: 'stated',
  value: { kind: 'money', paise: '48000' },
  sources: [{ kind: 'message', message_id: M1, quote: '480 each' }],
  needs_review: false,
  confirmed_at: null,
  confirmed_by: null,
  ...over,
});

test('every state has a symbol-class and a word', () => {
  assert.deepEqual(logic.statusView('stated'), { cls: 'clear', word: 'Clear' });
  assert.deepEqual(logic.statusView('unclear'), { cls: 'ambiguous', word: 'Ambiguous' });
  assert.deepEqual(logic.statusView('contradicted'), { cls: 'conflict', word: 'Conflict' });
  assert.deepEqual(logic.statusView('missing'), { cls: 'missing', word: 'Missing' });
  assert.throws(() => logic.statusView('maybe'));
});

test('values are described in words', () => {
  assert.equal(logic.describeValue({ kind: 'money', paise: '48000' }), 'Rs 480');
  assert.equal(logic.describeValue({ kind: 'money', paise: '4805' }), 'Rs 48.05');
  assert.equal(logic.describeValue({ kind: 'quantity', amount: '200', unit: null }), '200');
  assert.equal(logic.describeValue({ kind: 'quantity', amount: '200', unit: 'shirts' }), '200 shirts');
  assert.equal(logic.describeValue({ kind: 'partial_date', month_day: '--11-15' }), '15 Nov (year needed)');
  assert.equal(logic.describeValue({ kind: 'date', date: '2026-11-15' }), '2026-11-15');
  assert.equal(logic.describeValue({ kind: 'event', event: 'on_delivery' }), 'on delivery');
  assert.equal(logic.describeValue({ kind: 'text', text: 'Bilal' }), 'Bilal');
  assert.equal(logic.describeValue({ kind: 'duration', amount: 30, unit: 'days' }), '30 days');
  assert.equal(logic.describeValue(null), 'Not mentioned');
});

test('source labels are message positions', () => {
  assert.deepEqual(logic.sourceLabels(term(), messages), ['#1']);
  const two = term({ sources: [
    { kind: 'message', message_id: M2, quote: null },
    { kind: 'message', message_id: M1, quote: null },
  ] });
  assert.deepEqual(logic.sourceLabels(two, messages), ['#2', '#1']);
  assert.deepEqual(logic.sourceLabels(term({ sources: [] }), messages), []);
  assert.deepEqual(
    logic.sourceLabels(term({ sources: [{ kind: 'voice', voice_note_id: M1, start_ms: 0, end_ms: 5, quote: null }] }), messages),
    ['voice'],
  );
  assert.throws(() => logic.sourceLabels(term({ sources: [{ kind: 'message', message_id: ME, quote: null }] }), messages));
});

test('only a stated term with a full value can be confirmed', () => {
  assert.equal(logic.canConfirm(term()), true);
  assert.equal(logic.canConfirm(term({ state: 'unclear', value: null })), false);
  assert.equal(logic.canConfirm(term({ state: 'contradicted', value: null })), false);
  assert.equal(logic.canConfirm(term({ state: 'missing', value: null, sources: [] })), false);
  assert.equal(logic.canConfirm(term({ value: { kind: 'partial_date', month_day: '--11-15' } })), false);
  assert.equal(logic.canConfirm(term({ confirmed_at: '2026-10-25T11:00:00+05:30' })), false);
});

test('a confirmed term is built from the AI term, the user and the time', () => {
  const at = '2026-10-25T11:00:00+05:30';
  assert.deepEqual(logic.toAgreedTerm(term(), ME, at), {
    key: 'unit_price',
    value: { kind: 'money', paise: '48000' },
    sources: [{ kind: 'message', message_id: M1, quote: '480 each' }],
    confirmed_by: ME,
    confirmed_at: at,
  });
  assert.throws(() => logic.toAgreedTerm(term({ state: 'unclear', value: null }), ME, at));
  assert.throws(() => logic.toAgreedTerm(term(), ME, '2026-10-25T05:30:00Z'));
});

test('timestamps keep the local offset, have whole seconds and never end in Z', () => {
  const date = new Date(2026, 9, 25, 11, 0, 7, 450);
  const text = logic.timestampNow(date);
  assert.match(text, /^2026-10-25T11:00:07[+-]\d{2}:\d{2}$/);
  assert.ok(!text.endsWith('Z'));
  const offset = -date.getTimezoneOffset();
  const sign = offset < 0 ? '-' : '+';
  const abs = Math.abs(offset);
  const hh = String(Math.floor(abs / 60)).padStart(2, '0');
  const mm = String(abs % 60).padStart(2, '0');
  assert.ok(text.endsWith(`${sign}${hh}:${mm}`));
});

test('the primary user is the participant marked is_me', () => {
  assert.equal(logic.primaryUser([{ id: 'a', is_me: false }, { id: ME, is_me: true }]), ME);
  assert.throws(() => logic.primaryUser([{ id: 'a', is_me: false }]));
});

test('a receipt is summarised with its demo label', () => {
  const summary = logic.summariseReceipt({
    demo: true,
    receipt: { body: { spec_version: 'demo-skeleton-not-for-evidence', leaf_count: 6, root: 'ab'.repeat(32), chain: [{ version_n: 1, link: 'cd'.repeat(32) }] }, receipt_hash: 'ef'.repeat(32) },
  });
  assert.equal(summary.demo, true);
  assert.deepEqual(summary.rows.map((r) => r[0]), ['Recording type', 'Messages recorded', 'Merkle root', 'Version 1 link', 'Receipt hash']);
});
