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
