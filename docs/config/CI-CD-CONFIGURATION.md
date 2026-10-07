# Phase 5 — CI/CD Configuration Matrix

## Backend workflow

Repository: `s1xte3n/sixteen-resume-backend`

| Configuration | Type | GitHub location | Used by | Purpose |
|---|---|---|---|---|
| PYTHON_VERSION=3.12 | non-secret | workflow env | CI | Test/runtime alignment |
| NODE_VERSION=22 | non-secret | workflow env | CI | Azurite/tooling |
| ARM_TEMPLATE=infra/azure/azuredeploy.json | non-secret | workflow env | deployment | IaC source |
| PACKAGE_FILE=released-package.zip | non-secret | workflow env | deployment | package artifact |
| AZURE_CLIENT_ID | non-secret OIDC identifier | production environment variable | deployment | OIDC client input |
| AZURE_TENANT_ID | non-secret OIDC identifier | production environment variable | deployment | OIDC tenant input |
| AZURE_SUBSCRIPTION_ID | non-secret OIDC identifier | production environment variable | deployment | OIDC subscription input |
| AZURE_RESOURCE_GROUP | non-secret | production environment variable | deployment | target RG |
| AZURE_LOCATION | non-secret | production environment variable | deployment | East US |
| FRONTEND_STORAGE_ACCOUNT_NAME | non-secret | production environment variable | ARM | frontend Storage resource |
| FUNCTION_STORAGE_ACCOUNT_NAME | non-secret | production environment variable | ARM | Function host storage |
| DEPLOYMENT_STORAGE_ACCOUNT_NAME | non-secret | production environment variable | ARM | Flex deployment source |
| DEPLOYMENT_STORAGE_CONTAINER_NAME | non-secret | production environment variable | ARM | deployment container |
| FUNCTION_PLAN_NAME | non-secret | production environment variable | ARM | Flex plan |
| FUNCTION_APP_NAME | non-secret | production environment variable | ARM | Function App |
| COSMOS_ACCOUNT_NAME | non-secret | production environment variable | ARM | Cosmos account |
| COSMOS_TABLE_NAME | non-secret | production environment variable | ARM/runtime | VisitorCounter |
| CORS_ALLOWED_ORIGIN | non-secret | production environment variable | ARM/runtime | exact frontend origin |

Backend required stages:
1. Python install.
2. deterministic tests.
3. ARM structure validation.
4. Azurite persistence/concurrency tests.
5. local Functions HTTP contract tests.
6. OIDC login.
7. Azure/Flex availability validation.
8. ARM provider-contract validation.
9. ARM validation.
10. ARM deployment.
11. Flex configuration/RBAC verification.
12. package deployment.
13. runtime/API smoke verification.
14. evidence upload.

## Frontend workflow

Repository: `s1xte3n/sixteen-resume-frontend`

| Configuration | Type | GitHub location | Used by | Purpose |
|---|---|---|---|---|
| AZURE_CLIENT_ID | protected identifier | production environment variable | OIDC | frontend UAMI client ID |
| AZURE_TENANT_ID | protected identifier | production environment variable | OIDC | tenant |
| AZURE_SUBSCRIPTION_ID | protected identifier | production environment variable | OIDC | subscription |
| AZURE_RESOURCE_GROUP_NAME | non-secret | production environment variable | deploy/verify | Storage RG |
| AZURE_STORAGE_ACCOUNT_NAME | non-secret | production environment variable | deploy/verify | frontend Storage |
| AZURE_FRONTEND_IDENTITY_NAME | non-secret | production environment variable | OIDC verification | frontend UAMI |
| AZURE_FRONTEND_IDENTITY_RESOURCE_GROUP | non-secret | production environment variable | OIDC verification | UAMI RG |
| PUBLIC_HOSTNAME | non-secret | production environment variable | workflow/release | public hostname |
| VERIFY_PUBLIC_ENDPOINT | non-secret boolean | production environment variable | deploy | controls public endpoint verification |

Frontend deployment stages:
1. Validate production configuration and static artifacts.
2. Scan static output for credential material.
3. Build static output.
4. OIDC login.
5. upload `$web` using Entra authorization.
6. verify Storage static website endpoint.
7. verify public HTTPS only when edge is provisioned.
8. upload evidence.

## OIDC requirements

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` are identifiers, not credential secrets. They are supplied as protected production environment variables. No client secret, certificate, publish profile, SAS token, Cosmos key, or Storage connection string is required.

- GitHub workflow permission: `id-token: write`.
- No client secret.
- Federated credential subject must be exact production environment subject.
- Backend and frontend identities are separate.
- Deployment permissions remain scoped to the required Azure resources.


## Live OIDC subject correction — 2026-10-07

The production GitHub OIDC assertion format observed for this account is `repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`. The backend verifier now derives this form from GitHub owner/repository IDs. The configured backend federated credential already uses this observed subject.

Current backend client ID: `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d`; service-principal object ID `81822715-5de5-4bb5-8d70-e78f3fb55c1b`.

## 2026-10-07 controlled frontend OIDC verification correction

Live evidence now confirms the frontend user-assigned managed identity exists and the protected GitHub production variables have been populated:

- UAMI: `sixteen-resume-frontend-github`
- Client ID: `2d19e037-cc57-462c-a950-862f9b8a80e6`
- Principal ID: `200b60d9-b05a-4733-81f4-1053834de5c3`
- Federated credential issuer: `https://token.actions.githubusercontent.com`
- Federated credential subject: `repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production` was superseded by the live immutable subject `repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`.
- Federated credential audience: `api://AzureADTokenExchange`
- Frontend production `AZURE_CLIENT_ID`: `2d19e037-cc57-462c-a950-862f9b8a80e6`

The controlled workflow subsequently demonstrated that the frontend identity itself can authenticate only after Azure federation matches the exact live subject. Storage RBAC verification must use data-plane operations; a `Storage Blob Data Contributor` assignment does not grant `Microsoft.Storage/storageAccounts/read`, so `az storage account show` is not an appropriate least-privilege verification step.

Phase 5 remains **NOT PASSED** until a fresh frontend controlled workflow run succeeds from the corrected workflow revision and the remaining production edge/CORS/cost gates are independently evidenced.