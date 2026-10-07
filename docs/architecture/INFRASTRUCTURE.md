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

## Blockers
1. Backend GitHub must use the newly recreated application/client ID; current failures still show the retired principal.
2. Backend deployment identity must retain scoped RBAC administration so ARM roleAssignments can be created.
3. Frontend storage upload authorization is present, but `sixteen-resume.mooo.com` currently times out; Front Door/DNS routing is not yet proven.
