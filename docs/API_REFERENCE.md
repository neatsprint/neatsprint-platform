# API Reference

The merged OpenAPI 3.1 document is generated from every running service:

```bash
python scripts/docs/export_openapi.py
```

- Interactive reference: open `docs/api.html` (Redoc, loads `openapi.json`).
- Raw spec: `docs/openapi.json`.
- Service-local docs: `http://localhost:<port>/docs` (for example IAM `8001`, Task `8003`).
- Gateway base URL: `http://localhost:8000/api/v1`.

Regenerate after any contract change and commit both `openapi.json` and the service that changed.

## Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-REF-01**: Add a CI check in `platform-ci.yml` (or contract-ci) that verifies
  `docs/openapi.json` is valid OpenAPI 3.1 and has no unresolved `$ref` pointers.
- [ ] **IMP-REF-02**: Serve or link the interactive API reference from the developer documentation
  index and keep `neatsprint-contracts` synced with `docs/openapi.json` on every service release.
