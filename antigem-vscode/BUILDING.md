# Building AntiElite for VS Code

This document is for reviewers and contributors. It explains how the native Go bridge binary is produced and how the per-platform VSIX packages are built.

For what the extension runs, which ports, files and network it uses, and where each part of the source lives, see [ARCHITECTURE.md](ARCHITECTURE.md).

## What ships in the extension

- `dist/extension.js` + `dist/webview/**` — the extension host and webview UI (built by esbuild + Vite).
- `bin/antielite-bridge-<platform>-<arch>[.exe]` — the Go bridge (one file per target platform).
- `bridge/` source, `src/`, `shared/`, `webview/src/` — included for transparency.

The bridge is a fork of the AntiElite app's IDE bridge. It is a single static Go binary (`CGO_ENABLED=0`), binds only to `127.0.0.1`, and uses a CSRF token file under `~/.antielite_bridge/`. It never modifies the agy binary (started with `--no-agy-patch`).

## Supported targets (64-bit only)

| VS Code target | GOOS/GOARCH | Binary name |
|---|---|---|
| linux-x64 | linux/amd64 | `bin/antielite-bridge-linux-x64` |
| linux-arm64 | linux/arm64 | `bin/antielite-bridge-linux-arm64` |
| darwin-x64 | darwin/amd64 | `bin/antielite-bridge-darwin-x64` |
| darwin-arm64 | darwin/arm64 | `bin/antielite-bridge-darwin-arm64` |
| win32-x64 | windows/amd64 | `bin/antielite-bridge-win32-x64.exe` |

32-bit platforms are not supported.

## Prerequisites

- Node.js >= 20
- Go >= 1.22
- (For packaging) `@vscode/vsce` (installed via `npm install`)

## Build steps

```sh
npm install

# 1. Build the Go bridge for all 64-bit platforms:
npm run build:bridge

# 2. Build the extension host + webview:
npm run build

# Or both:
npm run build:all
```

## Package per platform

The Marketplace serves a separate VSIX per platform so each install stays small.
Each VSIX contains only its own bridge binary.

```sh
# Single target:
npm run package:linux-x64
npm run package:darwin-arm64
npm run package:win32-x64
# ...

# All targets:
npm run package:all
```

### Single VSIX for all platforms (optional)

If you prefer one package containing every platform's binary, build all binaries and run:

```sh
npm run package:single
```

This produces `antielite.vsix` (~30 MB) containing all five binaries.
It is under the Marketplace's ~100 MB limit, but per-platform packages are still recommended for
smaller downloads and faster installs.

Packaging temporarily moves the other platform binaries out of `bin/` and restores them afterwards, so `bin/` always ends up with all binaries again.

## Development

```sh
npm run watch:host          # rebuild extension host on change
npm run dev:webview         # Vite dev server for the UI
npm run dev:server -- /path/to/project   # host on ws://127.0.0.1:5199
npm run typecheck           # TypeScript check
```

## Runtime resolution

`src/extension.ts` resolves the binary as:

```
bin/antielite-bridge-${process.platform}-${process.arch}${win32 ? '.exe' : ''}
```

If the matching binary is missing, the extension reports "Bridge binary not found" and the bridge will not start.

## Optional: shrinking the binary

The bridge is ~13–14 MB per platform after `-s -w` (stripped). A per-platform VSIX is ~8.5 MB total
(binary + dist + source).

You can shrink the binary further with UPX (https://upx.github.io/), typically to ~4–6 MB:

```sh
upx --best --lzma bin/antielite-bridge-<target>[.exe]
```

Caveats:
- UPX-packed executables are frequently flagged by antivirus and by Marketplace reviewers as suspicious.
- UPX does not always work on macOS arm64 signed binaries without re-signing.
- Recommended only for local/personal builds, not for Marketplace publishing. Shipped binaries in this repo's
  releases are **not** UPX-compressed.

## The AntiElite Chrome extension

Plain MV3 files, no build step. It is **its own repository**, checked out next to this one as
`../antielite-chrome-extension` (or set `ANTIELITE_CHROME_EXTENSION=<folder>`). `npm run build:host` (`esbuild.mjs`) copies
it into `dist/chrome-extension`, which the VSIX ships; it warns and leaves it out when the folder is missing. In the app,
Settings → Browser copies it on to `~/.antielite/chrome-extension` (stable across extension updates) for *Load unpacked*
and registers the native messaging host. The dev server and `dev/test-browser-e2e.ts` use the sibling folder directly.

- **Extension id** `kbdjcdlfeoijcchepbldpldeaeijgibi`, pinned by the public `key` in its `manifest.json`
  (`src/core/browser/constants.ts` must match). The private key is **not** in the repo: `~/.antielite/chrome-extension.pem`
  (PKCS#8, made once with node crypto). Lose it and a packed/Web Store build gets another id.
- **Native host** `com.antielite.browser_bridge` = `bin/antielite-bridge-<platform>-<arch> --native-host` (wrapper
  `~/.antielite/chrome/antielite-native-host`), relaying Chrome's stdin/stdout to the VS Code window's Unix socket
  (`$XDG_RUNTIME_DIR/antielite/browser.sock`, else `~/.antielite/run/browser.sock`; `ANTIELITE_BROWSER_SOCKET` overrides).
  Windows: no wrapper. The manifest `~/.antielite/chrome/com.antielite.browser_bridge.json` names the `.exe` and is found
  through `HKCU\Software\<browser>\NativeMessagingHosts\com.antielite.browser_bridge`. The link is a named pipe
  `\\.\pipe\antielite-browser-<random>`, whose name is in `~/.antielite/run/browser.pipe` (`ANTIELITE_BROWSER_SOCKET` may
  name a pipe). Not yet tested on a Windows PC.
- **Pack a CRX later** (same id as the unpacked one):

```sh
google-chrome --pack-extension="$PWD/../antielite-chrome-extension" --pack-extension-key="$HOME/.antielite/chrome-extension.pem"
# -> antielite-chrome-extension.crx next to the folder. For the Chrome Web Store, zip the folder instead (remove "key" if the
#    store assigns its own id, then put that id in constants.ts and the host manifest's allowed_origins).
```

- **Tests**: `dev/test-browser.ts` (offline: framing, socket, routing, schemas) and `dev/test-browser-e2e.ts` (a throwaway
  Chrome for Testing profile with the native host manifest inside `<user-data-dir>/NativeMessagingHosts`, every tool
  against a local page and example.com; see the header of each file for the command).

## Related projects

- This extension is the VS Code port of the **AntiElite Android app**: https://github.com/santoshkurmi/antigem
- Extension repository: https://github.com/santoshkurmi/antigem_vscode_extension

Both share the same Go bridge protocol, chat UI and agent backends (agy, Claude Code, Codex, OpenCode); this project
just hosts them inside VS Code instead of on a phone.

## Security notes for reviewers

- The bridge listens on `127.0.0.1` only (configurable port, default 1244).
- All requests require a CSRF token from `~/.antielite_bridge/csrf_token.txt`.
- The agy hub is started with its standard `x-codeium-csrf-token` header; the agy binary is never patched (`--no-agy-patch`).
- Every AntiElite binary ships inside the VSIX. The only code downloaded at runtime is what the user asks for: official agent CLI installers (Install / Update buttons) and plugins the user installs.
- Source code is included in the package for verification.
