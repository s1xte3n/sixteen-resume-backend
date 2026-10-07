# Artifact Index

## Phase 3 — Architecture

| Artifact | Status | Scope |
|---|---|---|
| docs/architecture/ARCHITECTURE.md | Updated | System/component boundaries and required production flows |
| docs/architecture/INFRASTRUCTURE.md | Updated | Azure resources, identities, deployment boundaries, blockers |
| docs/architecture/SECURITY-ARCHITECTURE.md | Updated | OIDC, RBAC, storage and public-edge security |
| docs/architecture/ADR-INDEX.md | Updated | Architecture decisions |
| docs/architecture/ADR-004.md | Added | Frontend HTTPS/custom-domain edge |
| docs/architecture/ADR-005.md | Added | CI deployment RBAC |
| docs/architecture/ADR-006.md | Added | HTTPS/CDN feasibility blocker and cost constraint |


## Phase 3 blocker correction — 2026-10-07

- **Application/data architecture:** unchanged and remains frozen.
- **Backend CI identity:** current recreated application is 4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d; RBAC must be rebound to its current service-principal object before production ARM deployment can succeed.
- **Frontend edge:** the temporary Azure Front Door Standard resource is not production-approved. Current pricing conflicts with the hard R100/month recurring Azure/cloud ceiling, so ADR-006 is reopened as a Phase 3 feasibility blocker.
- **Public hostname timeout:** expected until an approved edge/origin/route/custom-domain path exists; this is not evidence of a frontend application defect.


## Phase 3 blocker remediation — 2026-10-07

| Artifact | Status | Change |
|---|---|---|
| `docs/ci-cd/PHASE-3-BLOCKER-REMEDIATION.md` | Added | Records the recreated backend OIDC client, correct service-principal RBAC boundary, and remaining public-edge blocker. |
| Backend production OIDC | Corrected configuration | GitHub production `AZURE_CLIENT_ID` now targets client `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d`; federated subject must match the immutable production subject exactly. |
| Backend deployment RBAC | Action required | Deployment service principal requires Contributor + User Access Administrator at `rg-sixteen-resume-prod` so ARM can create managed-identity role assignments. |
| Public HTTPS edge | Blocked | Storage is deployable independently; the custom hostname remains blocked until the approved edge/DNS/HTTPS path exists and passes evidence. |

Phase 3 remains blocked only by the authenticated production deployment RBAC/OIDC evidence and the incomplete public HTTPS edge path. No API, application, or browser/Cosmos architecture change is introduced.


## Current deployment remediation — 2026-10-07

| Artifact | Status | Evidence / change |
|---|---|---|
| `infra/azure/azuredeploy.json` | Corrected on branch `fix/cosmos-table-rbac-api-version` | Cosmos Table `Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments` now uses API version `2024-08-15-preview`, required for Table RBAC support. |
| ARM validation | Previously passed | The template structure validated successfully before deployment; validation did not expose the provider-version incompatibility during the actual resource operation. |
| ARM deployment | Blocked by provider API version | Deployment `sixteen-resume-flex-190` failed specifically on Cosmos Table RBAC with `BadRequest`: API version `2023-04-15` is invalid/too old for RBAC support. |
| Backend runtime health | Blocked downstream | The observed `DEPENDENCY_UNAVAILABLE` / HTTP 503 responses are not treated as an application defect until the corrected infrastructure deployment completes and Cosmos RBAC is verified. |
| Frontend public endpoint | Pending | `VERIFY_PUBLIC_ENDPOINT=false` correctly prevents the custom-hostname check; the remaining frontend timeout is the mandatory Azure Storage static-website endpoint check and must be investigated separately. |

**Phase gate status:** remains **BLOCKED** pending merge/deployment of the corrected ARM template, successful post-deployment Function/Cosmos verification, and separate Storage static-site reachability evidence.


## Current deployment incident — 2026-10-07

| Artifact | Status | Evidence / change |
|---|---|---|
| `infra/azure/azuredeploy.json` | Corrected | Cosmos Table `tableRoleAssignments` uses `2024-08-15-preview`; Function App resource identity remains `SystemAssigned`; Flex deployment-storage authentication remains `SystemAssignedIdentity`. |
| `.github/workflows/backend-ci.yml` | Corrected on `fix/flex-rbac-verification` | Adds a provider-contract preflight and updates Cosmos Table RBAC verification to the supported API version. |
| Backend ARM deployment | Failed in `sixteen-resume-flex-190` | Failure was specifically Cosmos Table RBAC API version `2023-04-15`; this is infrastructure/provider configuration, not application logic. |
| Backend HTTP verification | Failed downstream | `DEPENDENCY_UNAVAILABLE` / HTTP 503 and timeout responses are consistent with the Function not having a usable Cosmos Table dependency after the failed infrastructure deployment. |
| Frontend Storage smoke test | Failed / timed out | Must be rerun after the backend ARM deployment successfully provisions the static website resource; no frontend application change is required. |
| Public hostname | Not a current application defect | `VERIFY_PUBLIC_ENDPOINT=false`; public HTTPS remains separately blocked by the unresolved approved edge/DNS path. |

**Phase gate:** **BLOCKED** until a fresh `main` production run proves successful ARM deployment, Function/Cosmos RBAC, API health, and frontend Storage static-site reachability.
