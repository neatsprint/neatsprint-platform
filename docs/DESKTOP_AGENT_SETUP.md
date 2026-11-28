# Desktop Agent Setup (Windows first)

How to prepare a Windows machine to build the NeatSprint desktop agent (`M3-T22..T36`,
ADR-019/ADR-020). macOS and Linux notes come later.

Scope: **build and run locally**. Runtime needs no admin rights; installers do.

---

## 1. Baseline versions

| Tool | Version | Why it is needed |
| :--- | :--- | :--- |
| Windows | 10/11 x64 | Tauri v2 target; Windows-first platform order |
| Visual Studio Build Tools 2022 | 17.14+ | MSVC v143 linker (`link.exe`) and C compiler |
| Windows 11 SDK | 10.0.22621+ | Windows APIs, WebView2 headers |
| WebView2 Runtime | Evergreen (158+) | Renders the Tauri UI (preinstalled on Windows 11) |
| Rust | stable `x86_64-pc-windows-msvc` | Tauri core, capture, crypto, SQLCipher |
| Rust components | `rustfmt`, `clippy` | Formatting and lint gate |
| Node.js | **22 LTS** | UI toolchain, parity with web and CI |
| npm | 10+ | Package manager (ADR-014 uses npm) |
| Git | any recent | Submodule already present |
| NASM + Strawberry Perl | 3.x / 5.x | Build OpenSSL when SQLCipher is vendored |
| WiX / NSIS | auto | `tauri build` downloads the bundler tools |

`@tauri-apps/cli` v2 is installed per project as a dev dependency, not globally.

Disk and time: roughly 8–10 GB for the toolchain, ~5–10 minutes for the first Tauri
build, ~10 minutes more the first time SQLCipher and OpenSSL compile.

---

## 2. Machine status at 2026-11-28 (installed)

| Check | Result |
| :--- | :--- |
| Windows 11 Pro, 12 cores, 88 GB free | ready |
| Rust `1.100.1`, host `x86_64-pc-windows-msvc` | ready |
| rustup `1.29.3`, `rustfmt` + `clippy` | ready |
| VS Build Tools `17.14.37906.3` with VC.Tools | ready |
| Windows SDK `10.0.26100.0` | ready |
| WebView2 `158.0.4370.45` | ready |
| Node `22.23.5` via nvm4w, npm `10.9.9` | ready |
| NASM `2.16.01`, Strawberry Perl `5.42.3` | ready |
| Git `2.55`, winget `1.29` | ready |
| `cargo build` link smoke test (`Hello, world!`) | pass |

`./scripts/check-desktop-prereqs.ps1` reprints this table live.

---

## 3. Install (Administrator PowerShell)

```powershell
# 1. Visual Studio 2022 Build Tools: MSVC v143 + Windows 11 SDK
winget install --id Microsoft.VisualStudio.2022.BuildTools -e --accept-package-agreements --accept-source-agreements `
  --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"

# 2. Rust toolchain manager
winget install --id Rustlang.Rustup -e --accept-package-agreements --accept-source-agreements

# 3. Native build helpers for OpenSSL (SQLCipher)
winget install --id NASM.NASM -e --accept-package-agreements --accept-source-agreements
winget install --id StrawberryPerl.StrawberryPerl -e --accept-package-agreements --accept-source-agreements

# 4. Node 22 LTS alongside the existing 24 (nvm for Windows)
nvm install 22
nvm use 22
```

Then open a **new** terminal and pin the MSVC toolchain:

```powershell
rustup default stable-x86_64-pc-windows-msvc
rustup component add rustfmt clippy
rustc -vV     # host: x86_64-pc-windows-msvc
cargo --version
```

Notes:

- `--includeRecommended` is what pulls the Windows SDK in; without it `tauri build` fails
  at link time with missing Windows libs.
- `rustup` writes to `%USERPROFILE%\.cargo\bin`; a new shell is required for `PATH`.
- No Developer Mode is needed on Windows (that is a macOS requirement).
- If you would rather not build OpenSSL, use a prebuilt `libsqlcipher` (vcpkg) and set
  `LIBSQLCIPHER_LIB_DIR`; then NASM and Perl are not needed. The vendored route is the
  default because it is reproducible in CI.

---

## 4. Verify

```powershell
./scripts/check-desktop-prereqs.ps1
```

The script reports each prerequisite as `OK` or `MISSING` with the exact fix. A green run
ends with `Desktop prerequisites look ready.`

Manual spot checks:

```powershell
cl        # only inside a "Developer PowerShell for VS 2022" session
rustup show
node --version    # v22.x
```

---

## 5. Scaffolding the app (first task: M3-T22)

`services/neatsprint-desktop` currently holds only docs and pre-commit config. Planned
layout:

```text
neatsprint-desktop/
├── package.json            # npm scripts, UI deps, @tauri-apps/cli
├── src/                    # React + TypeScript UI (Vite)
├── src-tauri/
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/default.json
│   └── src/                # Rust core, IPC commands, tray
└── .github/workflows/ci.yml
```

Suggested Rust dependencies (locked at scaffold time, not before):

| Area | Crate | Purpose |
| :--- | :--- | :--- |
| Shell | `tauri` v2, `tauri-plugin-single-instance`, `tauri-plugin-autostart`, `tauri-plugin-updater`, `tauri-plugin-opener` | Window, tray, single instance, updates |
| Async/serialisation | `tokio`, `serde`, `serde_json`, `thiserror` | Commands, sync worker |
| Local database | `rusqlite` + `bundled-sqlcipher-vendored-openssl` | Encrypted queue and cache |
| Key handling | `argon2`, `keyring` (Windows Credential Manager) | SQLCipher key, device key |
| Device identity | `ed25519-dalek`, `rand`, `base64` | Key pair, request signatures |
| IDs and HTTP | `uuid` (v7), `reqwest` (rustls) | Offline IDs, API client |
| Capture | `xcap`, `image`, `windows` | Multi-monitor, DPI-correct capture, idle APIs |
| Diagnostics | `tracing`, `tracing-subscriber` | Structured local logs, no PII |

UI: React, `@tauri-apps/api` and the plugin JS bindings; dev tooling Vite, TypeScript
strict, ESLint, Prettier, Vitest + Testing Library.

Configuration:

- `src-tauri/tauri.conf.json`: `productName` "NeatSprint Agent", identifier
  `com.neatsprint.agent`, `build.devUrl` `http://localhost:1420`,
  `frontendDist` `../dist`.
- API base: dev `http://localhost:8000/api/v1` (gateway), staging `http://localhost:8100/api/v1`.
  Keep it in a runtime settings store, not baked into the binary.
- Secrets never go in files: device private key and tokens in the OS keychain, SQLCipher
  key wrapped by it.

Security baseline to honour from the first commit (`SECURITY.md` §3.4, §6, §9):

1. Ed25519 device key pair on first run; private key in the keychain (TPM-backed where available).
2. Every request carries `X-Device-ID` plus the DPoP-style proof over method, path, body hash, nonce and timestamp.
3. SQLCipher AES-256 with an Argon2id-derived key, wrapped in the keychain; never on disk unwrapped.
4. Capture only while a timer runs, always with a visible indicator; no silent mode.
5. Readable transparency log of every event sent.
6. Remote suspend/revoke/wipe handled as signed commands.

---

## 6. CI

A `windows-latest` workflow in the desktop repo:

```yaml
- uses: dtolnay/rust-toolchain@stable
  with: { targets: x86_64-pc-windows-msvc, components: rustfmt, clippy }
- uses: Swatinem/rust-cache@v2
- uses: actions/setup-node@v4
  with: { node-version: 22, cache: npm }
- run: npm ci
- run: cargo fmt --check --manifest-path src-tauri/Cargo.toml
- run: cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings
- run: cargo test --manifest-path src-tauri/Cargo.toml
- run: npm run build
- run: npx tauri build --debug
```

`windows-latest` includes the C++ workload, WebView2 and Strawberry Perl. NASM may still
need `choco install nasm -y` before the SQLCipher build; confirm on the first run.

---

## 7. Troubleshooting

| Symptom | Cause and fix |
| :--- | :--- |
| `error: linker 'link.exe' not found` | VS Build Tools with the C++ workload is missing, or the SDK was skipped. Re-run the `--includeRecommended` install. |
| `Could not find 'cl.exe'` | Same as above; `cl` only exists inside a Developer PowerShell, which Tauri does not need. |
| OpenSSL build fails with `nasm not found` / `perl` errors | Install NASM and Strawberry Perl, then rebuild with a clean `target/`. |
| Blank window in dev | WebView2 Runtime missing or dev server not on `http://localhost:1420`. |
| First build very slow | Normal: Tauri plus SQLCipher and OpenSSL. Later builds are incremental; optionally add `sccache`. |
| Antivirus scanning slows builds | Exclude `src-tauri/target` from real-time scanning. |
| Port 1420 already in use | Change `devUrl` and the Vite port together. |

---

## 8. Definition of done for setup

- [ ] `scripts/check-desktop-prereqs.ps1` prints all OK
- [ ] `rustc -vV` shows the `msvc` host and `cargo --version` works in a fresh shell
- [ ] `node --version` is 22.x
- [ ] First `cargo check` inside a scaffolded `src-tauri` succeeds
- [ ] CI workflow added to `neatsprint-desktop` and green on an empty scaffold

After that, start `M3-T22` (workspace, tray, single instance, auto-start), then `M3-T23`
(login, device registration, key pair) and `M3-T24` (SQLCipher schema).
