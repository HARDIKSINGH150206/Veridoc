// Test helper for the end-to-end test: re-checks a demo record with the JavaScript primitives of
// apps/verify (INTEGRITY_SPEC section 10), independently of the Python that built it.
// Input: { record, recap }. Output: one boolean per check.
import { readFileSync } from 'node:fs';

import * as lib from '../../verify/integrity.mjs';

const { record, recap } = JSON.parse(readFileSync(0, 'utf8'));
const { receipt, version, leaf_rows: rows } = record;
const hex = lib.toHex;
const encoder = new TextEncoder();

const leaves = [];
let leavesOk = true;
for (const row of rows) {
  const digest = await lib.payloadDigest(encoder.encode(row.payload));
  const leaf = await lib.leafHash(lib.PREFIXES.MESSAGE, lib.bytesFromHex(row.salt), digest);
  leavesOk &&= hex(digest) === row.payload_digest && hex(leaf) === row.leaf_hash;
  leaves.push(leaf);
}
const root = await lib.merkleRoot(leaves);
const termsSet = {
  deal_id: version.deal_id,
  version_n: version.version_n,
  playbook: version.playbook,
  terms: [...version.terms].sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0)),
};
const digest = await lib.termsDigest(termsSet);
const [link] = await lib.chainLinks([[digest, root]]);
const [entry] = receipt.body.chain;
const recapDigest = await lib.recapHash({
  deal_id: recap.deal_id,
  version_n: recap.version_n,
  language: recap.language,
  lines: recap.lines,
  body_text: recap.body_text,
});

process.stdout.write(JSON.stringify({
  leaves: leavesOk,
  root: hex(root) === receipt.body.root,
  chain: entry.terms_digest === hex(digest) && entry.root === hex(root) && entry.link === hex(link),
  version: version.terms_digest === hex(digest) && version.link === hex(link),
  receipt: hex(await lib.receiptHash(receipt.body)) === receipt.receipt_hash,
  recap_hash: hex(recapDigest) === recap.recap_hash,
  echo_code: (await lib.deriveEchoCode(recapDigest)) === recap.echo_code.code
    && recap.text.endsWith(`CONFIRM ${recap.echo_code.code}`),
}));
