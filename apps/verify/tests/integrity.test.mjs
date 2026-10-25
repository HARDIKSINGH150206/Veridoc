// Reproduces every vector in test-vectors/integrity/ with the JavaScript primitives.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { test } from 'node:test';

import * as lib from '../integrity.mjs';

const dir = new URL('../../../test-vectors/integrity/', import.meta.url);
const load = (name) => JSON.parse(readFileSync(new URL(name, dir), 'utf8'));
const hex = lib.toHex;
const { fromHex, bytesFromHex } = lib;

test('every vector file is present', () => {
  const names = readdirSync(dir).filter((n) => n.endsWith('.json')).sort();
  assert.deepEqual(names, [
    'canonical.json', 'chain.json', 'domain.json', 'echo.json', 'leaves.json',
    'merkle.json', 'normalize.json', 'records.json', 'sha256.json', 'timestamp.json',
    'worked_example.json',
  ]);
});

test('sha256 vectors', async () => {
  for (const v of load('sha256.json').vectors) {
    assert.equal(hex(await lib.sha256(bytesFromHex(v.input_hex))), v.sha256, v.name);
  }
});

test('domain separation vectors, export digests and rejected prefixes', async () => {
  const data = load('domain.json');
  for (const v of data.vectors) {
    const parts = v.parts_hex.map(bytesFromHex);
    assert.equal(hex(await lib.domainHash(v.prefix, ...parts)), v.hash, v.name);
  }
  for (const v of data.export_digests) {
    assert.equal(hex(await lib.exportDigest(bytesFromHex(v.raw_hex))), v.export_digest, v.name);
  }
  for (const v of data.rejected) {
    await assert.rejects(lib.domainHash(v.prefix, ...v.parts_hex.map(bytesFromHex)), v.name);
  }
  assert.deepEqual(
    Object.values(lib.PREFIXES).sort((a, b) => a - b),
    data.vectors.map((v) => v.prefix).sort((a, b) => a - b),
  );
});

test('canonical JSON vectors (RFC 8785)', () => {
  for (const v of load('canonical.json').vectors) {
    const out = lib.canonicalBytes(lib.parseJsonStrict(v.input_json));
    assert.equal(hex(out), v.canonical_hex, v.name);
    assert.equal(new TextDecoder().decode(out), v.canonical_utf8, v.name);
  }
});

test('integers outside the safe range are rejected', () => {
  const rejected = load('canonical.json').rejected;
  assert.ok(rejected.length >= 5);
  for (const v of rejected) {
    assert.throws(() => lib.parseJsonStrict(v.input_json), lib.IntegrityError, v.name);
  }
  assert.doesNotThrow(() => lib.parseJsonStrict('[9007199254740991, -9007199254740991, 1e30]'));
});

test('text normalisation vectors', async () => {
  for (const v of load('normalize.json').vectors) {
    const out = lib.canonicalRecord(lib.parseJsonStrict(v.input_json));
    assert.equal(hex(out), v.canonical_hex, v.name);
    assert.equal(hex(await lib.sha256(out)), v.record_digest, v.name);
  }
});

test('leaf vectors', async () => {
  const data = load('leaves.json');
  for (const v of data.vectors) {
    const salt = bytesFromHex(v.salt_hex);
    if (v.kind === 'file') {
      const raw = bytesFromHex(v.payload_hex);
      assert.equal(hex(await lib.payloadDigest(raw)), v.payload_digest, v.name);
      assert.equal(hex(await lib.fileLeaf(v.prefix, salt, raw)), v.leaf, v.name);
    } else {
      const record = lib.parseJsonStrict(v.record_json);
      assert.equal(hex(await lib.payloadDigest(lib.canonicalRecord(record))), v.payload_digest);
      assert.equal(hex(await lib.recordLeaf(v.prefix, salt, record)), v.leaf, v.name);
    }
  }
  for (const v of data.rejected) {
    await assert.rejects(
      lib.leafHash(v.prefix, bytesFromHex(v.salt_hex), bytesFromHex(v.digest_hex)),
      v.name,
    );
  }
});

test('merkle roots and inclusion proofs', async () => {
  const data = load('merkle.json');
  const ex = data.node_example;
  assert.equal(hex(await lib.nodeHash(fromHex(ex.left), fromHex(ex.right))), ex.node);
  for (const tree of data.trees) {
    const leaves = tree.leaves.map(fromHex);
    const root = fromHex(tree.root);
    assert.equal(hex(await lib.merkleRoot(leaves)), tree.root, `n=${tree.leaf_count}`);
    for (const proof of tree.proofs) {
      const steps = await lib.inclusionProof(leaves, proof.index);
      assert.deepEqual(
        steps.map((s) => ({ sibling: hex(s.sibling), side: s.side })),
        proof.steps,
        `n=${tree.leaf_count} index=${proof.index}`,
      );
      assert.equal(await lib.verifyInclusion(leaves[proof.index], steps, root), true);
    }
  }
  for (const v of data.rejected) {
    await assert.rejects(lib.merkleRoot(v.leaves.map(bytesFromHex)), v.name);
  }
});

test('merkle proof checks (wrong leaf, root, side, sibling, length)', async () => {
  for (const c of load('merkle.json').proof_checks) {
    const steps = c.steps.map((s) => ({ sibling: fromHex(s.sibling), side: s.side }));
    assert.equal(await lib.verifyInclusion(fromHex(c.leaf), steps, fromHex(c.root)), c.valid, c.name);
  }
});

test('echo codes', async () => {
  const data = load('echo.json');
  for (const v of data.vectors) {
    if (v.recap_json) {
      const recap = lib.parseJsonStrict(v.recap_json);
      assert.equal(hex(await lib.recapHash(recap)), v.recap_hash, v.name);
    }
    assert.equal(await lib.deriveEchoCode(fromHex(v.recap_hash)), v.echo_code, v.name);
  }
  for (const v of data.code_normalisation) {
    assert.equal(lib.normalizeCode(v.input), v.normalized, JSON.stringify(v.input));
  }
  for (const v of data.rejected) {
    await assert.rejects(lib.deriveEchoCode(bytesFromHex(v.recap_hash_hex)), v.name);
  }
});

test('version chain', async () => {
  const data = load('chain.json');
  assert.equal(hex(lib.GENESIS_LINK), data.genesis);
  const pairs = [];
  for (const e of data.versions) {
    const digest = await lib.termsDigest(lib.parseJsonStrict(e.terms_json));
    assert.equal(hex(digest), e.terms_digest);
    pairs.push([digest, fromHex(e.root)]);
  }
  const links = await lib.chainLinks(pairs);
  assert.deepEqual(links.map(hex), data.versions.map((e) => e.link));
});

test('plain records', async () => {
  for (const v of load('records.json').vectors) {
    const record = lib.parseJsonStrict(v.record_json);
    assert.equal(hex(await lib.plainRecordHash(v.prefix, record)), v.hash, v.name);
  }
  await assert.rejects(lib.plainRecordHash(0x10, {}));
});

test('worked example of the specification', async () => {
  const ex = load('worked_example.json');
  const salts = ex.salts_hex.map(bytesFromHex);
  const leaves = [];
  for (let i = 0; i < ex.payloads.length; i += 1) {
    leaves.push(await lib.recordLeaf(lib.PREFIXES.MESSAGE, salts[i], ex.payloads[i]));
  }
  assert.deepEqual(leaves.map(hex), ex.leaves);
  assert.equal(hex(await lib.nodeHash(leaves[0], leaves[1])), ex.node_1_2);
  assert.equal(hex(await lib.merkleRoot(leaves)), ex.root);
  assert.equal(new TextDecoder().decode(lib.canonicalBytes(ex.payloads[0])), ex.payload_1_canonical);
});

test('timestamps: format, parse and rejections', () => {
  const data = load('timestamp.json');
  for (const v of data.format) {
    assert.equal(lib.formatTimestamp(v.fields), v.text, v.name);
    assert.deepEqual(lib.parseTimestamp(v.text), v.fields, v.name);
  }
  for (const v of data.rejected_text) {
    assert.throws(() => lib.parseTimestamp(v.text), lib.IntegrityError, v.name);
  }
  for (const v of data.rejected_fields) {
    assert.throws(() => lib.formatTimestamp(v.fields), lib.IntegrityError, v.name);
  }
});
