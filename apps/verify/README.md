Standalone verify page (vanilla JavaScript, WebCrypto SHA-256). Owner: Area 4 (Hardik); it must pass Area 3's test vectors.

Status: `integrity.mjs` holds the JavaScript implementation of the integrity primitives (hashing, canonical JSON through the pinned npm package `canonicalize`, text normalisation, salted leaves, Merkle root and inclusion proofs, echo code, version chain, plain records). The verify page itself (`verify.html`) is not built yet; when it is, `integrity.mjs` and the canonicalize library are inlined into the single file, with no CDN.

Run the tests (Node 22 or later):

```
cd apps/verify
npm ci
npm test
```

`tests/integrity.test.mjs` reproduces every vector in `test-vectors/integrity/`. Integer literals outside the safe range are rejected by `parseJsonStrict`, which reads the number's source text (it needs a JavaScript engine that supports the JSON.parse reviver `context.source`: Node 22, current Chrome, Edge and Safari; where it is missing the range check cannot run).
