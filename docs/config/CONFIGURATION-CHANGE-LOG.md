# Phase 5 — Configuration Change Log

| Date | Repository | Change | Reason | Impact |
|---|---|---|---|---|
| 2026-10-07 | backend | Added controlled manual OIDC verification workflow | Provide non-deploying live evidence for GitHub → Azure trust and deployment RBAC | No API/runtime behavior change |
| 2026-10-07 | backend | Added controlled live OIDC/Azure verification procedure | Separate configuration definition from live Azure evidence | No product behavior change |
| 2026-10-07 | backend | Confirmed OIDC identifiers are protected production environment variables | Align Phase 5 model with backend deployment workflow | No credential model change |
| 2026-10-07 | backend | Corrected OIDC verification boundary | Backend verification validates the backend Entra application/service principal; frontend UAMI verification belongs to the frontend repository | No architecture/API change |
| 2026-10-07 | backend | Recorded live frontend UAMI provisioning blocker | `sixteen-resume-frontend-github` was not found in the approved production resource group | Phase 5 gate remains blocked pending Azure provisioning |

| 2026-10-07 | backend | Recorded frontend UAMI recreation and corrected production federation | Azure-side identity was recreated under the approved identity model | Frontend client-ID synchronization and Storage RBAC remain verification blockers; no API/runtime change |


## Phase 5 live OIDC correction — 2026-10-07

The frontend controlled run exposed the live GitHub OIDC subject format used by this account. The observed immutable production subject is:

`repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`

The backend deployment identity already has the observed backend subject:

`repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`

Both repository verification workflows now derive the expected subject from GitHub owner/repository IDs rather than assuming the shorter `repo:owner/repo:environment:production` form. This aligns verification with the actual assertion presented to Azure without changing the approved OIDC architecture.

The frontend Azure federated credential remains the only identified OIDC mismatch and must be recreated with the exact observed frontend subject before the next live run.
