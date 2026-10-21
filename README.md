# BEAST Tracker (desktop)

Offline bug bounty progress tracker. Electron app with an encrypted local vault.

## Run
```
npm install --save-dev electron electron-builder
npm test          # vault encryption self-test
npm start
```
Build installers: `npm run dist` (Windows NSIS, macOS dmg, Linux AppImage).

## Security design
- **Vault:** data is stored in `beast-vault.enc` (in the app's userData folder), encrypted with AES-256-GCM. The key comes from your passphrase via scrypt (N=32768, r=8, p=1) with a random salt. A fresh random IV is used for every save and the GCM tag detects tampering. File permissions are 0600 and writes are atomic.
- **Passphrase:** minimum 12 characters, never stored. Only the derived key is held in memory while unlocked. A lost passphrase cannot be recovered.
- **Brute-force slowdown:** failed unlocks add an exponential delay (1s up to 60s).
- **Auto-lock:** after 1, 5, 15 or 30 minutes of inactivity, on OS screen lock and on suspend. Locking drops the key and clears data from the UI.
- **Electron hardening:** contextIsolation on, nodeIntegration off, sandbox on, no remote content, navigation and new windows blocked, all permission requests denied, devtools off in packaged builds, single instance. IPC handlers only accept calls from the app's own page and validate every argument and size.
- **CSP:** `default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:`. No network access at all (`connect-src` falls back to none). `'unsafe-inline'` for styles is needed because the UI sets style attributes; scripts are never inline.
- **Exports:** saved through a native dialog, limited to .md, .csv, .json and .txt. CSV cells are protected against formula injection. Note that "Save backup file" writes **unencrypted** JSON, so store it safely.
- **No localStorage:** nothing is written outside the vault except the auto-lock setting in `config.json`.

## Known limits
- The vault protects data at rest. Malware running as your user while the vault is unlocked can still read it.
- Pin and update Electron regularly. Consider code signing and Electron fuses for release builds.
- Windows SmartScreen and macOS Gatekeeper will warn on unsigned installers.
