# BEAST Tracker

An offline progress tracker for bug bounty hunters and penetration testers. Keep track of which applications, subdomains and functionality you have tested, what is still remaining, and what you found, all in one place.

> **Use only on targets you are authorized to test.** Follow each program's scope, rules and disclosure policy. This tool only organizes your own notes and checklists. It does not scan or attack anything.

## Features

- **Targets:** application, then subdomains, then functionalities (method + path). Click a status badge to cycle Untested, In Progress, Tested and Vuln Found. Every level shows a % complete bar.
- **Dashboard:** totals, tested vs remaining, progress per application, findings by OWASP Top 10 category, recent activity.
- **Findings:** title, severity, OWASP category, optionally linked to the exact endpoint (which is then marked Vuln Found).
- **Checklist:** 8,407 test cases in 220 categories, tracked separately per application.
- **Search, filters and bulk actions:** search path and notes, filter by status and method, apply a status to all visible items at once.
- **Notes:** a short note on every endpoint.
- **Activity log:** a timestamped history of every change.
- **Import:** subdomain lists, plain URLs, "METHOD URL" lines, Burp items XML, ZAP XML and HAR JSON. Only method and URL are read, so tokens, cookies and bodies are never stored.
- **Export:** Markdown report, Endpoints CSV and Findings CSV.
- **Themes:** Cyberpunk, Dark, Light or System.
- **Desktop app:** encrypted local vault, auto-lock, hardened Electron shell.

## Checklist contents

| Domain | Test cases |
|---|---|
| Core (OWASP Top 10 + Bugcrowd VRT, with P1 to P5 priorities and short how-to hints) | 167 |
| Web | 3,956 |
| API | 1,299 |
| Android | 1,005 |
| iOS | 952 |
| Thick Client | 941 |
| Web3 / Smart Contracts | 87 |
| **Total** | **8,407** |

- Priorities on Core items follow the Bugcrowd Vulnerability Rating Taxonomy 1.19 (P1 Critical to P5 Info). A range such as P4-P1 means the rating depends on impact. Always follow the program's own severity policy.
- Core items carry CWE tags for cross-referencing with NVD. Tags marked `*` were not confirmed against the NVD list.
- Duplicates were removed within each domain. Identical wording in different domains is kept on purpose, since each domain is tested separately.

## Quick start (desktop)

Requires Node.js.

```
npm install --save-dev electron electron-builder
npm test        # vault encryption self-test
npm start
```

Build installers with `npm run dist` (Windows NSIS, macOS dmg, Linux AppImage).

On first run you create a vault passphrase (12+ characters). **A lost passphrase cannot be recovered.**

## Web version

`beast-tracker.html` is a single self-contained file. Open it in a browser. Data is kept in that browser's local storage and can be exported or restored from the Backup / Restore screen.

## Security design

- **Encrypted vault:** data is stored in `beast-vault.enc`, encrypted with AES-256-GCM. The key is derived from your passphrase with scrypt (N=32768, r=8, p=1) and a random salt. A new random IV is used for every save, and the GCM tag detects tampering. Files are written atomically with 0600 permissions.
- **Brute-force slowdown:** failed unlocks add an exponential delay (1s up to 60s).
- **Auto-lock:** after 1, 5, 15 or 30 minutes of inactivity, when the screen locks, and on suspend. Locking drops the key from memory and clears the UI.
- **Electron hardening:** contextIsolation on, nodeIntegration off, sandbox on, navigation and new windows blocked, all permission requests denied, devtools disabled in packaged builds, single instance. IPC handlers accept calls only from the app's own page and validate every argument and size.
- **Content-Security-Policy:** `default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:`. There is no network access. Inline styles are allowed only because the UI sets style attributes.
- **Input handling:** all user text is inserted as plain text (no `innerHTML`), lengths are capped, hostnames are validated, and imports are validated and sanitized.
- **Export safety:** CSV cells starting with `=`, `+`, `-` or `@` are prefixed to prevent formula injection. Markdown special characters are escaped.

### Known limits

- The vault protects data at rest. Malware running as your user while the app is unlocked can still read it.
- "Save backup file" writes unencrypted JSON, so store it somewhere safe.
- Pin and update Electron regularly, and consider code signing for release builds. Unsigned installers trigger SmartScreen or Gatekeeper warnings.

## Project structure

```
main.js          Electron main process (vault, IPC, window hardening)
preload.js       Minimal, validated bridge to the UI
vault.js         scrypt + AES-256-GCM helpers
test-vault.js    Encryption round-trip and tamper tests
src/index.html   UI shell with strict CSP
src/app.js       Application logic and checklist data
src/style.css    Themes (Cyberpunk, Dark, Light)
```

## Roadmap

- [x] Core tracker, dashboard, findings
- [x] Notes, OWASP/VRT checklists, endpoint-linked findings
- [x] Search, filters, bulk actions, activity log
- [x] Burp/ZAP/HAR import, Markdown/CSV export
- [x] Desktop packaging with encrypted vault and auto-lock
- [x] Cyberpunk, Dark and Light themes
- [ ] Screenshots of every screen
- [ ] Web3 checklist expanded beyond the current 87 items

## Sources and credits

- Bugcrowd Vulnerability Rating Taxonomy (VRT) 1.19 for priorities
- OWASP Top 10 (2021) categories
- CWE / NVD weakness names
- OWASP Smart Contract Security guidance as a base for the Web3 items
- Web, API, Android, iOS and Thick Client checks were imported from a third-party checklist page supplied by the project author. **Confirm that source's license and attribution requirements before publishing this dataset.**

## License

Choose a license before publishing (for example MIT) and add a `LICENSE` file.
