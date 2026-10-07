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
1. **Backend OIDC identity drift:** the latest backend application/client ID is 4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d with service-principal object ID 2c7e98c4-660e-4fe0-8ded-d214866080f3. Earlier RBAC work was applied to a superseded service principal and must not be treated as valid for the current workflow identity.
2. **Backend deployment RBAC:** the current backend service principal must have Contributor plus a scoped authorization-management role capable of Microsoft.Authorization/roleAssignments/write at rg-sixteen-resume-prod before ARM can create managed-identity role assignments. Contributor alone cannot assign Azure RBAC roles.
3. **Frontend public edge:** sixteen-resume.mooo.com times out because the created Front Door endpoint is not yet wired to an approved origin/route/custom domain.
4. **Edge cost feasibility:** Azure Front Door Standard is not approved because its current fixed base charge conflicts with the project's R100/month recurring Azure/cloud ceiling. ADR-006 is therefore a Phase 3 architecture blocker; do not finish or retain Front Door as production infrastructure until the budget/hosting/deviation decision is explicitly resolved.


## Phase 3 blocker correction — current

- Backend GitHub Actions identity is recreated and the production deployment identity is now the current client/service-principal pair recorded above.
- Backend deployment RBAC is scoped to the production resource group: Contributor for resource deployment plus User Access Administrator for the ARM-declared managed-identity role assignments. Owner is not used.
- The Function App production Cosmos Table client now explicitly uses the Function App system-assigned managed identity rather than the broader DefaultAzureCredential chain. The Cosmos Table audience remains `https://cosmos.azure.com`.
- The deployment workflow now fails immediately when the Cosmos Table data-plane role assignment is not visible for the current Function App identity, instead of continuing to an ambiguous HTTP smoke-test failure.
- The public frontend edge remains a separate Phase 3 feasibility blocker; no backend API or data architecture change is introduced.
