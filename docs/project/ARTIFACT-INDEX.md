## Phase 4 — API / Interface Contract

| Artifact | Status | Scope |
|---|---|---|
| docs/api/API-CONTRACT.md | Frozen / implementation-ready | Canonical VC-001 wire contract |
| docs/api/API-ENDPOINTS.md | Current | Public and internal interface inventory |
| docs/api/API-SCHEMAS.md | Current | Success, error, and persistence schemas |
| docs/api/API-ERRORS.md | Current | Canonical HTTP/error taxonomy |
| docs/api/API-VARIABLES.md | Current | Request/response headers and fields |
| docs/api/API-EXAMPLES.md | Current | Representative request/response examples |
| docs/api/API-CHANGELOG.md | Current | Contract version history |
| docs/api/openapi.yaml | Current | Machine-readable OpenAPI contract |
| docs/api/API-CONSISTENCY-REVIEW.md | Added | Cross-repository Phase 4 gate review |

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


## Phase 3 blocker correction — 2026-10-07

| Artifact | Status | Change |
|---|---|---|
| `src/infrastructure/factory.py` | Corrected on PR #51 | Production Cosmos Table access explicitly uses the Function App system-assigned managed identity. |
| `.github/workflows/backend-ci.yml` | Corrected on PR #51 | Cosmos Table RBAC propagation is now a hard prerequisite before HTTP readiness verification. |
| `docs/architecture/INFRASTRUCTURE.md` | Updated on PR #51 | Current backend deployment identity/RBAC and runtime identity boundary recorded. |
| `docs/architecture/SECURITY-ARCHITECTURE.md` | Updated on PR #51 | Current least-privilege identity boundary recorded. |
| `docs/architecture/ARCHITECTURE.md` | Updated on PR #51 | Frozen architecture explicitly separated from Phase 3 runtime/deployment verification corrections. |
| `docs/ci-cd/PHASE-3-BLOCKER-STATUS.md` | Updated on PR #51 | Current identity, RBAC, runtime and frontend dependency status recorded. |

The Phase 3 architecture remains unchanged. These are implementation/verification corrections only.


## Phase 3 blocker correction — 2026-10-07 (Flex provider contract)

| Artifact | Status | Change |
|---|---|---|
| `infra/azure/azuredeploy.json` | Corrected on `fix/phase3-flex-template-validation` | Function App resource API is now `Microsoft.Web/sites@2025-03-01`; the Function App managed identity remains `SystemAssigned`, while Flex deployment-storage authentication remains `SystemAssignedIdentity`. |
| Backend deployment identity | Corrected | Active GitHub OIDC client is `e3f56077-0aae-4a90-bde3-d0c0ef2a35e0`; service-principal object is `5eda2f89-4428-4c25-b93a-a1ddb1868864`; production RG permissions are Contributor + User Access Administrator. |
| Backend runtime readiness | Blocked | HTTP `503 DEPENDENCY_UNAVAILABLE` / timeout evidence remains downstream until the corrected ARM deployment succeeds and Cosmos Table RBAC is verified. |
| Frontend Storage verification | Blocked | Current frontend timeout is the Azure Storage static-site reachability check; public custom-domain HTTPS remains a separate edge decision. |

**Phase 3 gate remains BLOCKED.** The application/data architecture is unchanged. The remaining work is fresh deployment and runtime evidence after the provider-contract correction.


## Phase 5 — Variables, Environments & Secrets

| Artifact | Status | Scope |
|---|---|---|
| docs/config/ENVIRONMENT-VARIABLES.md | Added / canonical | Cross-system non-secret configuration inventory |
| docs/config/ENVIRONMENT-MATRIX.md | Added / canonical | Local, test, CI, deployment, production contexts |
| docs/config/SECRETS-MANAGEMENT.md | Added / canonical | OIDC, managed identity, credential elimination and handling |
| docs/config/TEST-DATA.md | Added / canonical | Generated test state and synthetic data |
| docs/config/CI-CD-CONFIGURATION.md | Added / canonical | Backend/frontend GitHub Actions configuration matrix |
| docs/config/CONFIGURATION-VALIDATION-RULES.md | Added / canonical | Pre-implementation configuration validation rules |
| docs/config/CONFIGURATION-DEPENDENCY-MAP.md | Added / canonical | Configuration dependency ordering |
| docs/config/CONFIGURATION-TRACEABILITY.md | Added / canonical | Requirement/contract/deployment/ADR/test traceability |
| docs/config/CONFIGURATION-SECURITY-REVIEW.md | Added / canonical | Configuration security findings and gates |
| docs/config/CONFIGURATION-CHANGE-LOG.md | Added | Phase 5 change history |

### Phase 5 gate status

**CONFIGURATION READY: NOT PASSED — configuration gates remain explicit.**

Resolved by this phase: runtime variable inventory, test-state separation, synthetic data strategy, OIDC/managed-identity credential model, CI/CD inputs, validation rules, dependency ordering, and traceability.

Remaining configuration gates: final HTTPS/edge service, final public hostname, final production CORS origin, live GitHub/Azure OIDC and RBAC evidence, live deployed endpoints, and production cost evidence <= R100/month.

No secret value is required in source control. No API route or schema was changed.
