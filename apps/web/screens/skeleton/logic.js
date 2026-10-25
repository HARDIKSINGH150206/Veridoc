// Logic of the walking-skeleton screen. Pure functions: no DOM, no network, no clock.
// Chat text is data: it is only ever shown with textContent, never as markup.

const STATUS = {
  stated: { cls: 'clear', word: 'Clear' },
  unclear: { cls: 'ambiguous', word: 'Ambiguous' },
  contradicted: { cls: 'conflict', word: 'Conflict' },
  missing: { cls: 'missing', word: 'Missing' },
};

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const PAISE_PER_RUPEE = 100n;
const WHOLE_SECOND_TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/;

export function statusView(state) {
  const view = STATUS[state];
  if (view === undefined) throw new Error(`unknown term state: ${state}`);
  return { ...view };
}

export function describeValue(value) {
  if (value === null || value === undefined) return 'Not mentioned';
  switch (value.kind) {
    case 'money': {
      const paise = BigInt(value.paise);
      const rupees = paise / PAISE_PER_RUPEE;
      const rest = paise % PAISE_PER_RUPEE;
      return rest === 0n ? `Rs ${rupees}` : `Rs ${rupees}.${String(rest).padStart(2, '0')}`;
    }
    case 'quantity':
      return value.unit ? `${value.amount} ${value.unit}` : value.amount;
    case 'partial_date': {
      const [, month, day] = /^--(\d{2})-(\d{2})$/.exec(value.month_day);
      return `${Number(day)} ${MONTHS[Number(month) - 1]} (year needed)`;
    }
    case 'date':
      return value.date;
    case 'event':
      return value.event.replaceAll('_', ' ');
    case 'duration':
      return `${value.amount} ${value.unit}`;
    case 'text':
      return value.text;
    default:
      throw new Error(`unknown value kind: ${value.kind}`);
  }
}

/** "#<position>" for each message source, "voice" for a voice clip. */
export function sourceLabels(term, messages) {
  return term.sources.map((source) => {
    if (source.kind === 'voice') return 'voice';
    const message = messages.find((m) => m.id === source.message_id);
    if (message === undefined) throw new Error('a source points at a message that is not in the chat');
    return `#${message.seq}`;
  });
}

/** Only a stated term with a full value that is not yet confirmed can be confirmed by the user. */
export function canConfirm(term) {
  return term.state === 'stated'
    && term.value !== null
    && term.value.kind !== 'partial_date'
    && term.confirmed_at === null;
}

/** The AgreedTerm the server accepts, built only from a term the user chose to confirm. */
export function toAgreedTerm(term, participantId, confirmedAt) {
  if (!canConfirm(term)) throw new Error('this term cannot be confirmed');
  if (!WHOLE_SECOND_TIMESTAMP.test(confirmedAt)) throw new Error('timestamps keep the offset and never end in Z');
  return {
    key: term.key,
    value: term.value,
    sources: term.sources,
    confirmed_by: participantId,
    confirmed_at: confirmedAt,
  };
}

const pad = (n) => String(n).padStart(2, '0');

/** YYYY-MM-DDTHH:MM:SS+HH:MM in the device's own offset, whole seconds, never Z. */
export function timestampNow(date) {
  const offset = -date.getTimezoneOffset();
  const sign = offset < 0 ? '-' : '+';
  const abs = Math.abs(offset);
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
    + `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    + `${sign}${pad(Math.floor(abs / 60))}:${pad(abs % 60)}`;
}

export function primaryUser(participants) {
  const me = participants.find((p) => p.is_me);
  if (me === undefined) throw new Error('no participant is marked as the primary user');
  return me.id;
}

/** Rows for the receipt view, with the demo label kept next to the hashes. */
export function summariseReceipt(record) {
  const { body, receipt_hash: hash } = record.receipt;
  const rows = [
    ['Recording type', body.spec_version],
    ['Messages recorded', String(body.leaf_count)],
    ['Merkle root', body.root],
    ...body.chain.map((c) => [`Version ${c.version_n} link`, c.link]),
    ['Receipt hash', hash],
  ];
  return { demo: record.demo === true, rows };
}

/** The badge text while the recorded fake model answers, otherwise null. */
export function modelBadgeText(mode) {
  return mode === 'fake' ? 'Demo mode: recorded model output' : null;
}
