// Walking skeleton screen: import a sample, confirm terms, get a recap and a receipt.
// All requests go to the local API on this device. Chat text is only shown with textContent.
import {
  canConfirm,
  describeValue,
  modelBadgeText,
  primaryUser,
  sourceLabels,
  statusView,
  summariseReceipt,
  timestampNow,
  toAgreedTerm,
} from './logic.js';

const apiBase = document.querySelector('meta[name="api-base"]').content;
const $ = (id) => document.getElementById(id);

const state = { sampleId: null, participants: [], messages: [], terms: [], confirmed: new Map() };

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function notify(message) {
  const box = $('notice');
  box.textContent = message ?? '';
  box.hidden = !message;
}

async function api(path, body) {
  const options = body === undefined
    ? {}
    : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
  const response = await fetch(`${apiBase}${path}`, options);
  if (response.status === 404) throw new Error('Not found. Demo mode is off: start VeriDoc with VERIDOC_DEMO_MODE=1.');
  if (!response.ok) {
    const detail = await response.json().then((d) => d.detail, () => null);
    throw new Error(typeof detail === 'string' ? detail : `The request failed (${response.status}).`);
  }
  return response.json();
}

function statusBadge(term) {
  const view = statusView(term.state);
  const badge = el('span', `status status--${view.cls}`);
  const symbol = el('span', 'status__symbol');
  symbol.setAttribute('aria-hidden', 'true');
  badge.append(symbol, document.createTextNode(view.word));
  return badge;
}

function renderChat() {
  const list = $('chat');
  list.replaceChildren();
  const names = new Map(state.participants.map((p) => [p.id, p.display_name]));
  for (const message of state.messages) {
    const item = el('li', 'message');
    item.id = `msg-${message.seq}`;
    item.append(el('span', 'message__meta', `${names.get(message.sender_id) ?? 'System'} · #${message.seq}`));
    item.append(el('span', '', message.text));
    list.append(item);
  }
  $('chat-count').textContent = `${state.messages.length} messages`;
}

function sourceLinks(term) {
  const box = el('div', 'terms__source');
  const labels = sourceLabels(term, state.messages);
  if (labels.length === 0) {
    box.textContent = 'No source';
    return box;
  }
  box.append(document.createTextNode('Source '));
  labels.forEach((label, index) => {
    if (index > 0) box.append(document.createTextNode(', '));
    if (label.startsWith('#')) {
      const link = el('a', '', label);
      link.href = `#msg-${label.slice(1)}`;
      box.append(link);
    } else {
      box.append(document.createTextNode(label));
    }
  });
  return box;
}

function renderTerms() {
  const list = $('terms');
  list.replaceChildren();
  for (const term of state.terms) {
    const item = el('li', 'terms__item');
    const head = el('div');
    head.append(el('div', 'terms__label', term.key.replaceAll('_', ' ')));
    head.append(el('div', 'terms__value', describeValue(term.value)));
    item.append(head, statusBadge(term), sourceLinks(term));
    if (term.needs_review) item.append(el('p', 'muted', 'Needs review: check the source before confirming.'));
    if (state.confirmed.has(term.key)) {
      item.append(el('p', 'muted', '✓ Confirmed by you'));
    } else if (canConfirm(term)) {
      const button = el('button', 'btn btn--small', 'Confirm this term');
      button.type = 'button';
      button.addEventListener('click', () => confirmTerm(term));
      item.append(button);
    } else if (term.state === 'stated') {
      item.append(el('p', 'muted', 'The year is needed before this date can be confirmed.'));
    }
    list.append(item);
  }
  $('make-recap').disabled = state.confirmed.size === 0;
}

function confirmTerm(term) {
  const agreed = toAgreedTerm(term, primaryUser(state.participants), timestampNow(new Date()));
  state.confirmed.set(term.key, agreed);
  $('record').disabled = true;
  renderTerms();
}

async function importSample() {
  notify('');
  const id = $('sample').value;
  const sample = await api(`/ingest/samples/${encodeURIComponent(id)}`);
  const analysis = await api(`/analysis/samples/${encodeURIComponent(id)}/terms`);
  Object.assign(state, {
    sampleId: id,
    participants: sample.participants,
    messages: sample.messages,
    terms: analysis.terms,
    confirmed: new Map(),
  });
  $('recap').textContent = '';
  $('echo').textContent = '';
  $('receipt').replaceChildren();
  $('receipt-label').textContent = '';
  $('record').disabled = true;
  renderChat();
  renderTerms();
}

function confirmedBody() {
  return { terms: [...state.confirmed.values()] };
}

async function makeRecap() {
  notify('');
  const recap = await api(`/agreement/samples/${encodeURIComponent(state.sampleId)}/recap`, confirmedBody());
  $('recap').textContent = recap.text;
  $('echo').textContent = `Echo code: ${recap.echo_code.code}`;
  $('record').disabled = false;
}

async function record() {
  notify('');
  const result = await api(`/vault/samples/${encodeURIComponent(state.sampleId)}/record`, confirmedBody());
  const summary = summariseReceipt(result);
  $('receipt-label').textContent = summary.demo
    ? 'Demo receipt: real hashes over a synthetic chat, labelled not for evidence.'
    : '';
  const list = $('receipt');
  list.replaceChildren();
  for (const [label, value] of summary.rows) {
    list.append(el('dt', '', label), el('dd', '', value));
  }
}

function guarded(action) {
  return () => action().catch((error) => notify(error.message));
}

async function start() {
  const health = await api('/health');
  const badgeText = modelBadgeText(health.model_mode);
  $('model-badge').textContent = badgeText ?? '';
  $('model-badge').hidden = badgeText === null;
  const { samples } = await api('/ingest/samples');
  const select = $('sample');
  for (const id of samples) select.append(new Option(id, id));
  $('import').addEventListener('click', guarded(importSample));
  $('make-recap').addEventListener('click', guarded(makeRecap));
  $('record').addEventListener('click', guarded(record));
}

start().catch((error) => notify(error.message));
