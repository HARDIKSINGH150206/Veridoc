// JavaScript implementation of the integrity primitives (docs/INTEGRITY_SPEC.md), for the
// standalone verify page. It must reproduce every vector in test-vectors/integrity/ exactly.
//
// Pure functions: bytes or JSON in, bytes or text out. SHA-256 uses WebCrypto (async). Canonical
// JSON uses the npm package `canonicalize` (RFC 8785), pinned in package.json. Hash operands are
// raw bytes (Uint8Array); hex is for storage and display only.

import canonicalize from 'canonicalize';

const encoder = new TextEncoder();

export const DIGEST_SIZE = 32;
export const SALT_SIZE = 16;

export const PREFIXES = Object.freeze({
  MERKLE_NODE: 0x01,
  MESSAGE: 0x10,
  VOICE_AUDIO: 0x11,
  TRANSCRIPT_SPAN: 0x12,
  HANDSHAKE_SEAL: 0x13,
  ATTACHMENT: 0x14,
  TERM: 0x15,
  IMPORT_RECORD: 0x16,
  TERMS_SET: 0x20,
  RECAP: 0x21,
  CONFIRMATION: 0x22,
  CHAIN_LINK: 0x30,
  RECEIPT: 0x40,
  ECHO: 0x50,
});

/** Records that selective disclosure could hide: salted leaves. */
export const SALTED_LEAF_PREFIXES = new Set([0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x22]);
/** Structural records hashed as H(prefix || canonical JSON), without salt. */
export const PLAIN_RECORD_PREFIXES = new Set([0x16, 0x20, 0x21, 0x40]);

const PREFIX_VALUES = new Set(Object.values(PREFIXES));

export const CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
export const GENESIS_LINK = new Uint8Array(32);

export class IntegrityError extends Error {
  constructor(message) {
    super(message);
    this.name = 'IntegrityError';
  }
}

// ---------------------------------------------------------------- bytes and hex

export function concat(...arrays) {
  const out = new Uint8Array(arrays.reduce((n, a) => n + a.length, 0));
  let offset = 0;
  for (const a of arrays) {
    out.set(a, offset);
    offset += a.length;
  }
  return out;
}

export function toHex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Parse hex text (any even length, lowercase or uppercase) into bytes. */
export function bytesFromHex(text) {
  if (!/^(?:[0-9a-fA-F]{2})*$/.test(text)) throw new IntegrityError('invalid hexadecimal text');
  return Uint8Array.from(text.match(/../g) ?? [], (h) => parseInt(h, 16));
}

/** Parse a 64-character lowercase hex hash. */
export function fromHex(text) {
  if (!/^[0-9a-f]{64}$/.test(text)) {
    throw new IntegrityError('expected 64 lowercase hexadecimal characters');
  }
  return bytesFromHex(text);
}

export function bytesEqual(a, b) {
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

function requireDigest(value, name) {
  if (!(value instanceof Uint8Array) || value.length !== DIGEST_SIZE) {
    throw new IntegrityError(`${name} must be ${DIGEST_SIZE} bytes`);
  }
  return value;
}

// ---------------------------------------------------------------- hashing

export async function sha256(bytes) {
  return new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes));
}

export function checkPrefix(prefix) {
  if (!PREFIX_VALUES.has(prefix)) {
    throw new IntegrityError(`unknown or reserved domain-separation prefix: ${prefix}`);
  }
  return prefix;
}

export async function domainHash(prefix, ...parts) {
  checkPrefix(prefix);
  for (const part of parts) {
    if (!(part instanceof Uint8Array)) throw new TypeError('hash operands must be bytes');
  }
  return sha256(concat(Uint8Array.of(prefix), ...parts));
}

/** Plain SHA-256 of the raw export file: no prefix, no normalisation. */
export async function exportDigest(rawExport) {
  return sha256(rawExport);
}

// ---------------------------------------------------------------- canonical JSON

/**
 * Parse JSON text and reject integer literals outside -(2^53 - 1) .. 2^53 - 1. The check reads
 * the source text of each number (JSON.parse reviver context), so it works even though the
 * parsed value would already have lost precision. Floats written with a point or exponent pass.
 */
export function parseJsonStrict(text) {
  return JSON.parse(text, (_key, value, context) => {
    if (typeof value === 'number' && context && /^-?\d+$/.test(context.source)) {
      const big = BigInt(context.source);
      const limit = BigInt(Number.MAX_SAFE_INTEGER);
      if (big > limit || big < -limit) {
        throw new IntegrityError(`integer outside the safe range: ${context.source}`);
      }
    }
    return value;
  });
}

/** RFC 8785 canonical UTF-8 bytes. Normalises nothing. */
export function canonicalBytes(value) {
  let text;
  try {
    text = canonicalize(value);
  } catch (error) {
    throw new IntegrityError(`cannot canonicalise: ${error.message}`);
  }
  if (typeof text !== 'string') throw new IntegrityError('cannot canonicalise this value');
  return encoder.encode(text);
}

/** Unicode NFC, then CRLF and lone CR become LF. */
export function normalizeText(text) {
  return text.normalize('NFC').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

/** A copy with normalizeText applied to every string value. Keys are never changed. */
export function normalizeStrings(value) {
  if (typeof value === 'string') return normalizeText(value);
  if (Array.isArray(value)) return value.map(normalizeStrings);
  if (value !== null && typeof value === 'object') {
    const out = {};
    for (const [key, item] of Object.entries(value)) out[key] = normalizeStrings(item);
    return out;
  }
  return value;
}

/** normalizeStrings, then canonicalBytes. */
export function canonicalRecord(value) {
  return canonicalBytes(normalizeStrings(value));
}

// ---------------------------------------------------------------- leaves and Merkle tree

export async function payloadDigest(payload) {
  return sha256(payload);
}

export async function leafHash(prefix, salt, digest) {
  if (!SALTED_LEAF_PREFIXES.has(prefix)) {
    throw new IntegrityError(`prefix ${prefix} is not a salted leaf record type`);
  }
  if (!(salt instanceof Uint8Array) || salt.length !== SALT_SIZE) {
    throw new IntegrityError(`salt must be ${SALT_SIZE} bytes`);
  }
  if (!(digest instanceof Uint8Array) || digest.length !== DIGEST_SIZE) {
    throw new IntegrityError(`payload digest must be ${DIGEST_SIZE} bytes`);
  }
  return domainHash(prefix, salt, digest);
}

export async function recordLeaf(prefix, salt, record) {
  return leafHash(prefix, salt, await payloadDigest(canonicalRecord(record)));
}

export async function fileLeaf(prefix, salt, raw) {
  return leafHash(prefix, salt, await payloadDigest(raw));
}

export async function nodeHash(left, right) {
  return domainHash(PREFIXES.MERKLE_NODE, left, right);
}

function checkLeaves(leaves) {
  if (leaves.length === 0) throw new IntegrityError('a Merkle tree cannot be empty');
  for (const leaf of leaves) {
    if (!(leaf instanceof Uint8Array) || leaf.length !== DIGEST_SIZE) {
      throw new IntegrityError(`every leaf must be ${DIGEST_SIZE} bytes`);
    }
  }
}

async function nextLevel(level) {
  const next = [];
  for (let i = 0; i + 1 < level.length; i += 2) next.push(await nodeHash(level[i], level[i + 1]));
  if (level.length % 2 === 1) next.push(level[level.length - 1]);
  return next;
}

export async function merkleRoot(leaves) {
  checkLeaves(leaves);
  let level = [...leaves];
  while (level.length > 1) level = await nextLevel(level);
  return level[0];
}

/** Sibling hashes from the leaf up to the root: [{ sibling, side }]. */
export async function inclusionProof(leaves, index) {
  checkLeaves(leaves);
  if (!Number.isInteger(index) || index < 0 || index >= leaves.length) {
    throw new IntegrityError('leaf index out of range');
  }
  const proof = [];
  let level = [...leaves];
  let position = index;
  while (level.length > 1) {
    if (position % 2 === 0) {
      if (position + 1 < level.length) proof.push({ sibling: level[position + 1], side: 'right' });
    } else {
      proof.push({ sibling: level[position - 1], side: 'left' });
    }
    level = await nextLevel(level);
    position = Math.floor(position / 2);
  }
  return proof;
}

/** True if the proof leads from the leaf to the root. Never throws on malformed input. */
export async function verifyInclusion(leaf, proof, root) {
  if (!(leaf instanceof Uint8Array) || leaf.length !== DIGEST_SIZE) return false;
  let current = leaf;
  for (const step of proof) {
    if (!(step.sibling instanceof Uint8Array) || step.sibling.length !== DIGEST_SIZE) return false;
    if (step.side === 'left') current = await nodeHash(step.sibling, current);
    else if (step.side === 'right') current = await nodeHash(current, step.sibling);
    else return false;
  }
  return bytesEqual(current, root);
}

// ---------------------------------------------------------------- echo code

export async function deriveEchoCode(recapHash) {
  const digest = await domainHash(PREFIXES.ECHO, requireDigest(recapHash, 'recap hash'));
  const bits = ((digest[0] << 16) | (digest[1] << 8) | digest[2]) >> 4;
  return [15, 10, 5, 0].map((shift) => CROCKFORD[(bits >> shift) & 31]).join('');
}

/** Trim, upper-case, O to 0, I and L to 1. Returns null if the result is not a valid code. */
export function normalizeCode(raw) {
  const code = raw.trim().toUpperCase().replace(/O/g, '0').replace(/[IL]/g, '1');
  return code.length === 4 && [...code].every((c) => CROCKFORD.includes(c)) ? code : null;
}

// ---------------------------------------------------------------- version chain and records

export async function termsDigest(termsSet) {
  return domainHash(PREFIXES.TERMS_SET, canonicalRecord(termsSet));
}

export async function chainLink(prevLink, digest, root) {
  const previous = prevLink == null ? GENESIS_LINK : requireDigest(prevLink, 'previous link');
  return domainHash(
    PREFIXES.CHAIN_LINK,
    previous,
    requireDigest(digest, 'terms digest'),
    requireDigest(root, 'root'),
  );
}

/** All links for a list of [termsDigest, root] pairs, version 1 first. */
export async function chainLinks(entries) {
  const links = [];
  let previous = null;
  for (const [digest, root] of entries) {
    previous = await chainLink(previous, digest, root);
    links.push(previous);
  }
  return links;
}

export async function plainRecordHash(prefix, record) {
  if (!PLAIN_RECORD_PREFIXES.has(prefix)) {
    throw new IntegrityError(`prefix ${prefix} is not a plain record type`);
  }
  return domainHash(prefix, canonicalRecord(record));
}

export const recapHash = (recap) => plainRecordHash(PREFIXES.RECAP, recap);
export const receiptHash = (receipt) => plainRecordHash(PREFIXES.RECEIPT, receipt);
export const importRecordHash = (record) => plainRecordHash(PREFIXES.IMPORT_RECORD, record);

// ---------------------------------------------------------------- timestamps in hashed records

const TIMESTAMP_FORM = /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([+-])([0-9]{2}):([0-9]{2})$/;

function daysInMonth(year, month) {
  if (month === 2) return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28;
  return [4, 6, 9, 11].includes(month) ? 30 : 31;
}

const isInt = (n) => Number.isInteger(n);
const pad = (n, width) => String(n).padStart(width, '0');

function checkTimestampFields(f) {
  const { year, month, day, hour, minute, second, offset_minutes: offset } = f;
  if (offset === null || offset === undefined) throw new IntegrityError('a timestamp needs an offset');
  if (f.microsecond) throw new IntegrityError('a timestamp has whole seconds only');
  if (![year, month, day, hour, minute, second, offset].every(isInt)) {
    throw new IntegrityError('timestamp fields must be integers');
  }
  const valid = year >= 1 && year <= 9999 && month >= 1 && month <= 12 && day >= 1
    && day <= daysInMonth(year, month) && hour <= 23 && hour >= 0 && minute >= 0 && minute <= 59
    && second >= 0 && second <= 59 && Math.abs(offset) < 24 * 60;
  if (!valid) throw new IntegrityError('not a real date and time');
}

/** Write fields {year, month, day, hour, minute, second, offset_minutes} as
 *  YYYY-MM-DDTHH:MM:SS+HH:MM. The offset is kept; there is no conversion to UTC and never a Z. */
export function formatTimestamp(f) {
  checkTimestampFields(f);
  const sign = f.offset_minutes < 0 ? '-' : '+';
  const abs = Math.abs(f.offset_minutes);
  return `${pad(f.year, 4)}-${pad(f.month, 2)}-${pad(f.day, 2)}T${pad(f.hour, 2)}:${pad(f.minute, 2)}:${pad(f.second, 2)}`
    + `${sign}${pad(Math.floor(abs / 60), 2)}:${pad(abs % 60, 2)}`;
}

/** Read the exact written form into fields. Rejects Z, a missing offset, fractional seconds,
 *  -00:00 and impossible dates or times. */
export function parseTimestamp(text) {
  const m = TIMESTAMP_FORM.exec(text);
  if (m === null) throw new IntegrityError('not in the form YYYY-MM-DDTHH:MM:SS+HH:MM');
  const [year, month, day, hour, minute, second] = m.slice(1, 7).map(Number);
  const hours = Number(m[8]);
  const minutes = Number(m[9]);
  if (hours > 23 || minutes > 59) throw new IntegrityError('the offset is out of range');
  const total = hours * 60 + minutes;
  if (m[7] === '-' && total === 0) throw new IntegrityError('a zero offset is written +00:00');
  const fields = { year, month, day, hour, minute, second, offset_minutes: m[7] === '-' ? -total : total };
  checkTimestampFields(fields);
  return fields;
}
