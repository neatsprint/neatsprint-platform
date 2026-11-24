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
