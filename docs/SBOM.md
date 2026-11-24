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

## Residual risk

- Base images are mutable tags (`python:3.12-slim`, `node:22-alpine`). Rebuild regularly and
  re-run the gate; pin digests when the release process moves to a registry with retention.
- `--ignore-unfixed` hides findings with no upstream patch. They are tracked by Dependabot and
  reviewed at each release.
