# Phase 5 — Configuration Security Review

## Findings

| ID | Area | Status | Finding / required control |
|---|---|---|---|
| SEC-CFG-001 | Browser credential exposure | PASS | Browser receives no Cosmos, Azure, Storage, Function, or deployment credentials. |
| SEC-CFG-002 | Cosmos direct access | PASS | Browser calls only GET /api/visitors; Cosmos access remains backend-only. |
| SEC-CFG-003 | Runtime database credential | PASS | Function uses system-assigned managed identity + Cosmos Table RBAC; no connection string/key. |
| SEC-CFG-004 | CI authentication | PASS | GitHub Actions uses OIDC; no long-lived Azure client secret. |
| SEC-CFG-005 | Frontend deployment auth | PASS | Frontend uploads through Entra authorization, not storage keys/SAS. |
| SEC-CFG-006 | Backend deployment permissions | WARNING | Current architecture requires scoped Contributor + authorization-management permission because ARM creates role assignments; live RBAC evidence is still a gate. |
| SEC-CFG-007 | Git history | PASS | Project rule prohibits credentials in tracked files; workflow scans frontend artifacts. |
| SEC-CFG-008 | Logs/evidence | PASS | Secrets must not be printed or uploaded; Azure CLI output must avoid credential material. |
| SEC-CFG-009 | CORS | TBD / configuration gate | Exact final origin cannot be frozen until public edge/hostname is approved. Wildcard is prohibited. |
| SEC-CFG-010 | Public API abuse/rate limiting | TBD / contract/platform gate | API contract recognizes platform/runtime 429 but no project-approved configurable application rate-limit value exists. Do not invent one. |
| SEC-CFG-011 | Edge/CDN | TBD / configuration gate | Exact production HTTPS/CDN service remains unresolved under ADR-006 and cost ceiling. |
| SEC-CFG-012 | Production cost | TBD / configuration gate | R100/month is the hard ceiling; live cost evidence is required. |
| SEC-CFG-013 | Test/production separation | PASS | Automated persistence uses Azurite and generated test tables; production counter is not test state. |
| SEC-CFG-014 | Placeholder values | PASS | Production validation must reject unresolved placeholders rather than silently deploying them. |

## Blocker policy

No blocker is silently resolved. A configuration gate remains open until live evidence or an approved source-of-truth decision closes it.
