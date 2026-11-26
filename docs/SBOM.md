# SBOM and Container Scan — 2026-11-24

Tool: Trivy **0.69.3** (last safe release before the 0.69.4 supply-chain compromise).
Scan mode: `--severity HIGH,CRITICAL --ignore-unfixed` against each locally built image.
SBOMs are CycloneDX JSON in `docs/sbom/`.

## Result

| Image | Ecosystem | High/Critical |
| :--- | :--- | ---: |
| `neatsprint-neatsprint-web` | Node 22 alpine | **0** |
| `neatsprint-neatsprint-core` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-iam` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-task` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-team` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-worklog` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-monitoring` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-reports` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-chat` | Python 3.12 slim | **0** |
| `neatsprint-neatsprint-ai` | Python 3.12 slim | **0** |

## Findings fixed during the scan

- **Web image, 10 high in npm's own bundled CLI dependencies** (`brace-expansion`,
  `ip-address`, `pacote`, `picomatch`, `sigstore`). The runtime only needs `node server.js`, so
  the runner stage now removes `/usr/local/lib/node_modules/npm` and the `npm`/`npx` shims.
  Rescan: 0.
- **Six Python images, 57 high in Debian `krb5`/`zlib` packages.** Those images predated the
  refreshed `python:3.12-slim` base; rebuilding picked up the patched base packages. Rescan: 0.

## Reproduce

```bash
docker save neatsprint-neatsprint-web:latest -o /tmp/web.tar
docker run --rm -v /tmp:/work -v trivy-cache:/root/.cache/trivy \
  aquasec/trivy:0.69.3 image --input /work/web.tar \
  --severity HIGH,CRITICAL --ignore-unfixed --scanners vuln
```

The release workflow (`.github/workflows/release.yml`) runs the same gate with
`aquasecurity/trivy-action@0.35.0` and uploads a per-image SPDX SBOM.

## Residual Risk & Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-SBM-01 (Pin base image digests)**: Base images currently use mutable tags
  (`python:3.12-slim`, `node:22-alpine`). Pin `@sha256:...` digests in every `Dockerfile` and
  refresh monthly via Dependabot (`IMP-OPS-02`).
- [ ] **IMP-SBM-02 (Generate CycloneDX SBOMs for all 10 images locally)**: `docs/sbom/` currently
  commits `web.cdx.json` and `core.cdx.json` as representative artefacts (while `.github/workflows/release.yml`
  generates SPDX SBOMs for all 10 images in CI). Add a helper script `scripts/security/export_sboms.py`
  to regenerate all 10 local SBOMs on demand.
- [ ] **IMP-SBM-03 (Track unfixed base-OS advisories)**: `--ignore-unfixed` hides Debian/Alpine
  CVEs that have no upstream patch yet; review unfixed high/critical findings at each release.
