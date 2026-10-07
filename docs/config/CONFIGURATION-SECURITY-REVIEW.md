# Phase 5 — Configuration Security Review

## Findings

| ID | Area | Status | Finding / required control |
|---|---|---|---|
| SEC-CFG-001 | Browser credential exposure | PASS | Browser receives no Cosmos, Azure, Storage, Function, or deployment credentials. |
| SEC-CFG-002 | Cosmos direct access | PASS | Browser calls only GET /api/visitors; Cosmos access remains backend-only. |
| SEC-CFG-003 | Runtime database credential | PASS | Function uses system-assigned managed identity + Cosmos Table RBAC; no connection string/key. |
| SEC-CFG-004 | CI authentication | PASS | GitHub Actions uses OIDC; no long-lived Azure client secret is approved. |
| SEC-CFG-005 | Frontend deployment auth | PASS | Frontend deployment uses Entra authorization rather than Storage keys/SAS. |
| SEC-CFG-006 | Backend deployment permissions | WARNING | Approved boundary is scoped Contributor + authorization-management permission; live RBAC evidence is still required. |
| SEC-CFG-007 | Git history | PASS | Project rule prohibits credentials in tracked files; frontend workflow scans published artifacts. |
| SEC-CFG-008 | Logs/evidence | PASS | Secrets must not be printed or uploaded; Azure CLI output must avoid credential material. |
| SEC-CFG-009 | Backend/frontend OIDC separation | PASS | Backend uses the approved Entra application/service principal; frontend uses its separate user-assigned managed identity. Verification paths are repository-specific. |
| SEC-CFG-010 | Frontend UAMI provisioning | PASS | Approved UAMI `sixteen-resume-frontend-github` now exists in `rg-sixteen-resume-prod`; client ID and principal ID are recorded in the frontend Phase 5 artifacts. |
| SEC-CFG-011 | GitHub production configuration | WARNING | `AZURE_FRONTEND_IDENTITY_NAME` has been configured. Frontend `AZURE_CLIENT_ID` still requires synchronization to the newly provisioned UAMI client ID before the controlled workflow can pass. |
| SEC-CFG-012 | CORS | TBD / configuration gate | Exact final origin cannot be frozen until public edge/hostname is approved. Wildcard is prohibited. |
| SEC-CFG-013 | Public API abuse/rate limiting | TBD / contract/platform gate | No project-approved application rate-limit value exists. Do not invent one. |
| SEC-CFG-014 | Edge/CDN | TBD / configuration gate | Exact production HTTPS/CDN service remains unresolved under ADR-006 and the cost ceiling. |
| SEC-CFG-015 | Production cost | TBD / configuration gate | R100/month is the hard ceiling; live cost evidence is required. |
| SEC-CFG-016 | Test/production separation | PASS | Automated persistence uses synthetic/Azurite state; production counter is not test state. |
| SEC-CFG-017 | Placeholder values | PASS | Production validation must reject unresolved placeholders rather than silently deploying them. |

## Required remediation

1. Keep backend and frontend OIDC verification separate.
2. Verify the backend `AZURE_CLIENT_ID` as an Entra application/service principal, not as a user-assigned managed identity.
3. Provision the approved frontend UAMI `sixteen-resume-frontend-github` in the approved production-resource-group boundary.
4. Configure its exact GitHub production federated credential and Storage Blob Data Contributor assignment.
5. Add the required frontend production environment variables, including `AZURE_FRONTEND_IDENTITY_NAME`.
6. Rerun the frontend controlled verification workflow.
7. Record live evidence before closing the Phase 5 configuration gate.

No secret, client secret, Storage key, SAS token, Cosmos key, or browser credential is introduced.

## Blocker policy

No blocker is silently resolved. A configuration gate remains open until live evidence or an approved source-of-truth decision closes it.


## Current OIDC correction — 2026-10-07

- **Backend client ID:** current reported value is `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d`; the previously recorded `e3f56077-0aae-4a90-bde3-d0c0ef2a35e0` is superseded.
- **Backend live verification:** pending. The local `az identity show` check was invalid for the backend because the approved backend deployment identity is an Entra application/service principal, not a user-assigned managed identity.
- **Frontend live verification:** blocked because `AZURE_FRONTEND_IDENTITY_NAME` is missing from the GitHub `production` environment and `sixteen-resume-frontend-github` is absent from Azure at the tested resource-group scope.
- **Phase 5 gate:** NOT PASSED.

## Live correction — 2026-10-07

- Frontend UAMI: `sixteen-resume-frontend-github` exists in `rg-sixteen-resume-prod`.
- Frontend client ID: `2d19e037-cc57-462c-a950-862f9b8a80e6`.
- Frontend principal ID: `200b60d9-b05a-4733-81f4-1053834de5c3`.
- Federated credential subject: `repo:s1xte3n/sixteen-resume-frontend:environment:production`.
- Frontend GitHub `AZURE_FRONTEND_IDENTITY_NAME` is configured.
- Storage RBAC remains unverified because local `az role assignment` commands return `MissingSubscription`.
- Phase 5 remains NOT PASSED until protected client-ID synchronization and Storage RBAC are proven by the controlled frontend workflow.
