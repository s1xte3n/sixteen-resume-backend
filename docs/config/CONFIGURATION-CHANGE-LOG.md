# Phase 5 — Configuration Change Log

## 2026-10-07 — Phase 5 baseline

- Added canonical backend configuration inventory.
- Added explicit separation of local/test/CI/deployment/production contexts.
- Added secret/credential inventory with OIDC and managed-identity elimination rules.
- Added generated test state and synthetic test-data inventory.
- Added backend/frontend CI/CD configuration matrix.
- Added configuration validation rules and dependency graph.
- Added requirement/API/deployment/ADR/test traceability.
- Added configuration-security review.
- Corrected frontend configuration documentation so the approved frontend does **not** claim a configurable `PUBLIC_API_BASE_URL` or `PUBLIC_API_PATH`; current frontend JavaScript uses same-origin `/api/visitors), which is frozen by VC-001.
- Kept the final public hostname, HTTPS edge service, CORS origin, live OIDC/RBAC evidence, and production cost as explicit configuration gates.
- No API route, request/response schema, persistence model, identity model, or deployment architecture was redesigned.

## 2026-10-07 — OIDC identifier classification correction

- Reclassified `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` from GitHub Environment Secrets to protected GitHub Environment Variables in the backend deployment workflow.
- Confirmed these values are OIDC identifiers, not client credentials.
- Preserved GitHub production environment protection and Microsoft Entra OIDC authentication.
- No long-lived Azure credential was introduced.
- Live GitHub/Azure configuration remains externally verifiable only through the protected environment and successful workflow evidence.
