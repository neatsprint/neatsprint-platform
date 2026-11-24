# Sub-processors

> **Draft — verify contracts and regions before publication.** Last updated: 2026-11-24.

| Sub-processor | Service | Data | Region | Safeguards |
| :--- | :--- | :--- | :--- | :--- |
| Cloud infrastructure provider | Hosting, managed Postgres, object storage, KMS | All tenant data | **[region]** | DPA, SCCs, encryption at rest |
| Email delivery provider | Transactional email (invitations, resets, assignment digests) | Email address, name, item references | **[region]** | DPA, TLS, no tracking pixels |
| Error monitoring provider (opt-in) | Crash reports with PII scrubbing | Diagnostic metadata | **[region]** | DPA, opt-in, scrubbing |
| Payment provider (when enabled) | Billing | Billing contact, invoice metadata | **[region]** | DPA, PCI DSS |
| Status page provider | Public incident communication | Incident text only | **[region]** | DPA |

Screenshot blobs are stored only in the configured object storage and are never sent to analytics,
AI or email providers. AI features (Phase 3) will use a separately listed provider and explicit
tenant opt-in.

Customers are notified before a new sub-processor starts processing personal data and may object
on reasonable data-protection grounds.
