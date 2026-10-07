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

## 2026-10-07 controlled frontend OIDC verification correction

Live evidence now confirms the frontend user-assigned managed identity exists and the protected GitHub production variables have been populated:

- UAMI: `sixteen-resume-frontend-github`
- Client ID: `2d19e037-cc57-462c-a950-862f9b8a80e6`
- Principal ID: `200b60d9-b05a-4733-81f4-1053834de5c3`
- Federated credential issuer: `https://token.actions.githubusercontent.com`
- Federated credential subject: `repo:s1xte3n/sixteen-resume-frontend:environment:production` was superseded by the live immutable subject `repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`.
- Federated credential audience: `api://AzureADTokenExchange`
- Frontend production `AZURE_CLIENT_ID`: `2d19e037-cc57-462c-a950-862f9b8a80e6`

The controlled workflow subsequently demonstrated that the frontend identity itself can authenticate only after Azure federation matches the exact live subject. Storage RBAC verification must use data-plane operations; a `Storage Blob Data Contributor` assignment does not grant `Microsoft.Storage/storageAccounts/read`, so `az storage account show` is not an appropriate least-privilege verification step.

Phase 5 remains **NOT PASSED** until a fresh frontend controlled workflow run succeeds from the corrected workflow revision and the remaining production edge/CORS/cost gates are independently evidenced.