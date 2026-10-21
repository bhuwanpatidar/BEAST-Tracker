'use strict';
const assert = require('assert'), crypto = require('crypto'), { kdf, enc, dec } = require('./vault');
const salt = crypto.randomBytes(16), key = kdf('correct horse battery', salt);
const blob = JSON.parse(enc(key, salt, '{"apps":[]}'));
assert.strictEqual(dec(key, blob), '{"apps":[]}');
assert.throws(() => dec(kdf('wrong passphrase!!', salt), blob));
blob.data = Buffer.from('tampered').toString('base64');
assert.throws(() => dec(key, blob));
console.log('vault tests passed');
