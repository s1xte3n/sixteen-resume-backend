# Infrastructure

## Production
| Resource | Name | Purpose |
|---|---|---|
| Resource group | rg-sixteen-resume-prod | Production boundary |
| Frontend Storage | st16resumeweb | Static website origin |
| Function Storage | st16resumefunc | Function host storage |
| Deployment Storage | st16resumedeploy | Flex deployment source |
| Function plan | sixteen-resume-functions | Flex Consumption FC1 |
| Function App | func-sixteen-resume | Visitor API |
| Cosmos DB | cosmos-sixteen-resume | Table API |
| Cosmos table | VisitorCounter | Visitor counter state |
| Public edge | Azure Front Door Standard/Premium | HTTPS/custom-domain ingress |

## Identity model
- Backend GitHub deployment identity: resource-group-scoped User Access Administrator or Role Based Access Control Administrator because ARM creates role assignments.
- Frontend GitHub deployment identity: Storage Blob Data Contributor scoped to `st16resumeweb`.
- Function managed identity: narrow data-plane roles only.

## Phase 3 Blockers
1. **Backend OIDC identity drift:** the active backend application/client ID is e3f56077-0aae-4a90-bde3-d0c0ef2a35e0 with service-principal object ID 5eda2f89-4428-4c25-b93a-a1ddb1868864. Earlier RBAC work was applied to a superseded service principal and must not be treated as valid for the current workflow identity.
2. **Backend deployment RBAC:** the current backend service principal must have Contributor plus a scoped authorization-management role capable of Microsoft.Authorization/roleAssignments/write at rg-sixteen-resume-prod before ARM can create managed-identity role assignments. Contributor alone cannot assign Azure RBAC roles.
3. **Frontend public edge:** sixteen-resume.mooo.com times out because the created Front Door endpoint is not yet wired to an approved origin/route/custom domain.
4. **Edge cost feasibility:** Azure Front Door Standard is not approved because its current fixed base charge conflicts with the project's R100/month recurring Azure/cloud ceiling. ADR-006 is therefore a Phase 3 architecture blocker; do not finish or retain Front Door as production infrastructure until the budget/hosting/deviation decision is explicitly resolved.


## Phase 3 blocker correction — current

- Backend GitHub Actions identity is recreated and the production deployment identity is now the current client/service-principal pair recorded above.
- Backend deployment RBAC is scoped to the production resource group: Contributor for resource deployment plus User Access Administrator for the ARM-declared managed-identity role assignments. Owner is not used.
- The Flex ARM site resource is pinned to `Microsoft.Web/sites@2025-03-01` to avoid the current ARM template-schema validation failure encountered with the previous site API version.
- The Function App production Cosmos Table client explicitly uses the Function App system-assigned managed identity rather than the broader DefaultAzureCredential chain. The Cosmos Table audience remains `https://cosmos.azure.com`.
- The deployment workflow now uses the `2026-03-15` Cosmos Table RBAC API consistently for provisioning and verification and fails immediately when the data-plane role assignment is not visible for the current Function App identity, instead of continuing to an ambiguous HTTP smoke-test failure.
- The public frontend edge remains a separate Phase 3 feasibility blocker; no backend API or data architecture change is introduced.
