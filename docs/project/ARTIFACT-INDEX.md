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
