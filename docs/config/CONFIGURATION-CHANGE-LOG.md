# Phase 5 — Configuration Change Log

| Date | Repository | Change | Reason | Impact |
|---|---|---|---|---|
| 2026-10-07 | backend | Added controlled manual OIDC verification workflow | Provide non-deploying live evidence for GitHub → Azure trust and deployment RBAC | No API/runtime behavior change |
| 2026-10-07 | backend | Added controlled live OIDC/Azure verification procedure | Separate configuration definition from live Azure evidence | No product behavior change |
| 2026-10-07 | backend | Confirmed OIDC identifiers are protected production environment variables | Align Phase 5 model with backend deployment workflow | No credential model change |
| 2026-10-07 | backend | Corrected OIDC verification boundary | Backend verification validates the backend Entra application/service principal; frontend UAMI verification belongs to the frontend repository | No architecture/API change |
| 2026-10-07 | backend | Recorded live frontend UAMI provisioning blocker | `sixteen-resume-frontend-github` was not found in the approved production resource group | Phase 5 gate remains blocked pending Azure provisioning |


## 2026-10-07 — Frontend OIDC verification correction

- Confirmed the frontend deployment identity is the UAMI `sixteen-resume-frontend-github`, not the previously tested backend-style identity.
- Recorded the provisioned frontend UAMI client ID `2d19e037-cc57-462c-a950-862f9b8a80e6`.
- Added the required frontend production identity resource-group variable.
- Corrected the frontend verification workflow to expect the standard GitHub environment subject `repo:s1xte3n/sixteen-resume-frontend:environment:production`.
- The malformed federated credential currently using owner/repository IDs must be replaced in Azure before live verification can pass.
- No API, persistence, runtime, or deployment architecture behavior changed.
