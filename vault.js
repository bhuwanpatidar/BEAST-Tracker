'use strict';
const crypto = require('crypto'), fs = require('fs');
// scrypt N=2^15, r=8, p=1 -> 256-bit key. AES-256-GCM with a fresh random 96-bit IV per write.
const kdf = (pw, salt) => crypto.scryptSync(pw, salt, 32, { N: 32768, r: 8, p: 1, maxmem: 64 * 1024 * 1024 });
function enc(key, salt, plain) {
  const iv = crypto.randomBytes(12), c = crypto.createCipheriv('aes-256-gcm', key, iv);
  const data = Buffer.concat([c.update(plain, 'utf8'), c.final()]);
  return JSON.stringify({ v: 1, salt: salt.toString('base64'), iv: iv.toString('base64'), tag: c.getAuthTag().toString('base64'), data: data.toString('base64') });
}
function dec(key, o) {
  const d = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(o.iv, 'base64'));
  d.setAuthTag(Buffer.from(o.tag, 'base64'));
  return Buffer.concat([d.update(Buffer.from(o.data, 'base64')), d.final()]).toString('utf8');
}
function writeAtomic(file, text) {
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, text, { mode: 0o600 });
  fs.renameSync(tmp, file);
}
module.exports = { kdf, enc, dec, writeAtomic };
