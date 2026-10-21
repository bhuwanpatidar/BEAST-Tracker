'use strict';
const { app, BrowserWindow, ipcMain, dialog, session, powerMonitor } = require('electron');
const path = require('path'), fs = require('fs'), crypto = require('crypto');
const { pathToFileURL } = require('url');
const { kdf, enc, dec, writeAtomic } = require('./vault');

const INDEX = pathToFileURL(path.join(__dirname, 'src', 'index.html')).href;
const EMPTY = '{"apps":[],"finds":[],"chk":{},"log":[]}';
const MAX = 50e6, MINUTES = [1, 5, 15, 30], EXT = ['.md', '.csv', '.json', '.txt'];
const VF = () => path.join(app.getPath('userData'), 'beast-vault.enc');
const CF = () => path.join(app.getPath('userData'), 'config.json');
let sess = null, timer = null, fails = 0, nextOk = 0, minutes = 5, win = null;

const lockNow = () => { sess = null; clearTimeout(timer); BrowserWindow.getAllWindows().forEach(w => w.webContents.send('vault:locked')); };
const arm = () => { clearTimeout(timer); if (sess) timer = setTimeout(lockNow, minutes * 60000); };
const goodPw = p => typeof p === 'string' && p.length >= 12 && p.length <= 256;
// Only the app's own page may call these handlers.
const H = (ch, fn) => ipcMain.handle(ch, (e, ...a) => {
  if (!e.senderFrame || e.senderFrame.url !== INDEX) throw new Error('denied');
  return fn(...a);
});

H('vault:status', () => ({ exists: fs.existsSync(VF()), unlocked: !!sess, minutes }));
H('vault:create', pw => {
  if (fs.existsSync(VF())) return { ok: false, err: 'A vault already exists.' };
  if (!goodPw(pw)) return { ok: false, err: 'Use 12 to 256 characters.' };
  const salt = crypto.randomBytes(16), key = kdf(pw, salt);
  writeAtomic(VF(), enc(key, salt, EMPTY));
  sess = { key, salt }; arm();
  return { ok: true, data: EMPTY };
});
H('vault:unlock', pw => {
  const wait = nextOk - Date.now();
  if (wait > 0) return { ok: false, err: 'Too many attempts. Wait ' + Math.ceil(wait / 1000) + 's.' };
  try {
    const o = JSON.parse(fs.readFileSync(VF(), 'utf8'));
    if (typeof pw !== 'string' || pw.length > 256) throw new Error('bad');
    const salt = Buffer.from(o.salt, 'base64'), key = kdf(pw, salt), data = dec(key, o);
    fails = 0; sess = { key, salt }; arm();
    return { ok: true, data };
  } catch (e) {
    fails++; nextOk = Date.now() + Math.min(60000, 1000 * 2 ** (fails - 1));
    return { ok: false, err: 'Wrong passphrase or damaged vault.' };
  }
});
H('vault:save', json => {
  if (!sess) return { ok: false };
  if (typeof json !== 'string' || json.length > MAX) return { ok: false };
  JSON.parse(json);
  writeAtomic(VF(), enc(sess.key, sess.salt, json));
  return { ok: true };
});
H('vault:lock', () => { lockNow(); return true; });
H('vault:activity', () => { arm(); return true; });
H('vault:minutes', m => {
  if (!MINUTES.includes(m)) return false;
  minutes = m; writeAtomic(CF(), JSON.stringify({ minutes })); arm(); return true;
});
H('vault:change', (oldPw, newPw, json) => {
  if (!sess || !goodPw(newPw) || typeof json !== 'string' || json.length > MAX) return { ok: false, err: 'Invalid request.' };
  const k = kdf(String(oldPw || ''), sess.salt);
  if (!crypto.timingSafeEqual(k, sess.key)) return { ok: false, err: 'Current passphrase is wrong.' };
  JSON.parse(json);
  const salt = crypto.randomBytes(16), key = kdf(newPw, salt);
  writeAtomic(VF(), enc(key, salt, json));
  sess = { key, salt };
  return { ok: true };
});
H('file:save', async (name, text) => {
  if (typeof text !== 'string' || text.length > MAX) return { ok: false };
  const base = path.basename(String(name)).replace(/[^\w.\-]/g, '_');
  if (!EXT.includes(path.extname(base).toLowerCase())) return { ok: false };
  const r = await dialog.showSaveDialog(win, { defaultPath: base, filters: [{ name: 'Export', extensions: EXT.map(x => x.slice(1)) }] });
  if (r.canceled || !r.filePath || !EXT.includes(path.extname(r.filePath).toLowerCase())) return { ok: false };
  fs.writeFileSync(r.filePath, text, { mode: 0o600 });
  return { ok: true };
});

function createWindow() {
  win = new BrowserWindow({
    width: 1280, height: 820, minWidth: 900, minHeight: 600, show: false, backgroundColor: '#0f1117',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false,
      sandbox: true, webSecurity: true, allowRunningInsecureContent: false, spellcheck: false, devTools: !app.isPackaged
    }
  });
  win.removeMenu();
  win.loadFile(path.join(__dirname, 'src', 'index.html'));
  win.once('ready-to-show', () => win.show());
}

app.on('web-contents-created', (_, wc) => {
  wc.setWindowOpenHandler(() => ({ action: 'deny' }));
  wc.on('will-navigate', e => e.preventDefault());
  wc.on('will-attach-webview', e => e.preventDefault());
});

if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } });
  app.whenReady().then(() => {
    try { const c = JSON.parse(fs.readFileSync(CF(), 'utf8')); if (MINUTES.includes(c.minutes)) minutes = c.minutes; } catch (e) {}
    session.defaultSession.setPermissionRequestHandler((_w, _p, cb) => cb(false));
    powerMonitor.on('lock-screen', lockNow);
    powerMonitor.on('suspend', lockNow);
    createWindow();
  });
  app.on('window-all-closed', () => app.quit());
}
