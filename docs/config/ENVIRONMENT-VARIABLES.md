# Phase 5 — Environment & Configuration Inventory

Status: **Phase 5 baseline — configuration model complete; controlled live OIDC/RBAC verification in progress**

This is the canonical cross-system configuration inventory. It does not redefine the API, architecture, or deployment model.

## Contexts

- **local** — developer execution with Azurite.
- **test** — automated tests using synthetic state/Azurite where applicable.
- **CI** — GitHub Actions validation.
- **deployment** — GitHub Actions Azure deployment.
- **production** — the single approved Azure deployment environment.

No additional Azure dev/test/staging environments are approved.

## Non-secret configuration

| ID | Name | Component | Contexts | Type | Required | Source/owner | Consumption | Constraints/default | Commit | GitHub Actions | Azure app config | ARM parameter | Generated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CFG-001 | APP_ENV | Function | local, test, production | enum | Yes | Backend/IaC owner | runtime | local for local execution; production in Azure | Name/value only if non-secret | Yes | Yes | No | No |
| CFG-002 | AZURE_LOCATION | Azure/CI | deployment, production | string | Yes | IaC owner | ARM + workflow | **eastus only** | Yes | Yes | No | Yes | No |
| CFG-003 | AZURE_RESOURCE_GROUP | Azure/CI | deployment, production | string | Yes | Azure owner | workflow | Must be approved RG: `rg-sixteen-resume-prod` | Value may be committed only if treated as public deployment metadata; workflow source currently uses GitHub environment variable | Yes | No | No | No |
| CFG-004 | FRONTEND_STORAGE_ACCOUNT_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow | Globally unique Azure Storage name; 3–24 chars | Name only; exact value is deployment-specific | Yes | Yes | No | Yes |
| CFG-005 | FUNCTION_STORAGE_ACCOUNT_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow | Globally unique Azure Storage name; 3–24 chars | Name only; exact value deployment-specific | Yes | Yes | No | Yes |
| CFG-006 | DEPLOYMENT_STORAGE_ACCOUNT_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow | Globally unique Azure Storage name; 3–24 chars | Name only; exact value deployment-specific | Yes | Yes | No | Yes |
| CFG-007 | DEPLOYMENT_STORAGE_CONTAINER_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | Flex deployment source | 3–63 chars; private blob container; approved default `function-deployments` | Yes | Yes | No | Yes | No |
| CFG-008 | FUNCTION_PLAN_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow | Approved Flex plan; current approved name `sixteen-resume-functions` | Yes | Yes | No | Yes | No |
| CFG-009 | FUNCTION_APP_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow/runtime | Azure Function App naming constraints; current approved name `func-sixteen-resume` | Yes | Yes | No | Yes | No |
| CFG-010 | COSMOS_ACCOUNT_NAME | Azure/CI | deployment, production | string | Yes | IaC owner | ARM/workflow | 3–50 chars; globally unique | Yes | Yes | No | Yes | No |
| CFG-011 | COSMOS_TABLE_NAME | Function/IaC | local, test, production | string | Yes | Backend/IaC owner | runtime + ARM | Current approved `VisitorCounter`; 3–63 chars | Yes | Yes | Yes | Yes | No |
| CFG-012 | CORS_ALLOWED_ORIGIN | Function/CI | deployment, production | origin URL | Yes | Cross-repo release owner | Function CORS + ARM validation | Exact final approved frontend origin; no wildcard | Value remains **TBD/configuration gate** until edge/hostname is approved | Yes as variable name; production value external | Yes | Yes | No |
| CFG-013 | COSMOS_ENDPOINT | Function | production | HTTPS URL | Yes | Azure/IaC owner | Function runtime | Must be Azure Cosmos Table endpoint; generated from deployed account | Name only; exact value generated | No fixed value | No | Yes | Yes |
| CFG-014 | COSMOS_PARTITION_KEY | Function/tests | local, test, production | string | Yes | Data model owner | persistence adapter | Current production logical key `VisitorCounter`; not client supplied | Yes | Optional | Yes | No | No |
| CFG-015 | COSMOS_ROW_KEY | Function/tests | local, test, production | string | Yes | Data model owner | persistence adapter | Current production logical key `Global`; not client supplied | Yes | Optional | Yes | No | No |
| CFG-016 | VISITOR_COUNTER_BACKEND | Function | local, test, production | enum | Yes | Backend owner | runtime factory | `memory` or `table`; production must use `table` | Yes | Yes | Yes | No | No |
| CFG-017 | AZURE_TABLE_CONNECTION_STRING | Function | local only | string | Yes for local table backend | Developer | Azurite TableServiceClient | Local synthetic connection string only; never production | **No value committed**; example may contain `UseDevelopmentStorage=true` | No | No | No | No |
| CFG-018 | AzureWebJobsStorage | Function | local, production | string | Platform setting | Azure Functions/IaC owner | Functions host | Local uses Azurite; production is intentionally empty because identity-based storage uses account name | Production value must not become a connection string | No | No | No | No |
| CFG-019 | AzureWebJobsStorage__accountName | Function | production | string | Yes | IaC owner | Functions host | Must equal FUNCTION_STORAGE_ACCOUNT_NAME | Name only | Yes as variable name | No | Yes | Yes |
| CFG-020 | FUNCTIONS_EXTENSION_VERSION | Function | local/test only if platform requires | string | No in production Flex | Azure Functions owner | Runtime | **Must not be used as a production Flex requirement**; current production verification expects it absent | Yes | No | No | No | No |
| CFG-021 | Python runtime | Function | production | version | Yes | IaC owner | Flex runtime | Python 3.12 | Yes | No | Yes via functionAppConfig | No | No |
| CFG-022 | Functions runtime | Function | production | version | Yes | IaC owner | Flex runtime | Functions v4 via functionAppConfig/runtime | Yes | No | Yes via ARM | No | No |
| CFG-023 | Flex instanceMemoryMB | Function | production | integer | Yes | IaC owner | Flex scale config | **512 MB** currently approved/provider-required | Yes | No | Yes via ARM | No | No |
| CFG-024 | Flex maximumInstanceCount | Function | production | integer | Yes | IaC owner | Flex scale config | **1** currently approved/provider-required | Yes | No | Yes via ARM | No | No |
| CFG-025 | Flex alwaysReady | Function | production | array | Yes | IaC owner | Flex scale config | Empty array for zero always-ready instances | Yes | No | Yes via ARM | No | No |
| CFG-026 | COSMOS audience | Function | production | URL | Yes | Backend security owner | Managed-identity Table client | `https://cosmos.azure.com` | Yes | No | No | No | No |
| CFG-026A | AZURE_CLIENT_ID | GitHub/Azure CI | deployment | UUID | Yes | Azure/GitHub identity owner | GitHub OIDC | Must match backend deployment identity client ID; current reported client ID: `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d` | No — identifier only | Yes | No | No | No |
| CFG-026B | AZURE_TENANT_ID | GitHub/Azure CI | deployment | UUID | Yes | Azure tenant owner | GitHub OIDC | Approved tenant UUID | No — identifier only | Yes | No | No | No |
| CFG-026C | AZURE_SUBSCRIPTION_ID | GitHub/Azure CI | deployment | UUID | Yes | Azure subscription owner | GitHub OIDC + Azure REST verification | Approved subscription UUID | No — identifier only | Yes | No | No | No |
| CFG-027 | PUBLIC_HOSTNAME | Frontend/DNS/CI | production | hostname | Yes | DNS/delivery owner | frontend workflow, release verification | Approved hostname; exact value **TBD/configuration gate** until edge/DNS decision | Name only; value deployment-specific | Yes | No | No | Yes |
| CFG-028 | VERIFY_PUBLIC_ENDPOINT | Frontend CI | production | boolean | Yes | Release owner | frontend workflow | false until approved edge/DNS exists; true only after edge acceptance | Yes | Yes | No | No | No |
| CFG-029 | PUBLIC_API_BASE_URL | Frontend | none currently | URL | No | — | Not consumed by current approved frontend | **Do not introduce**; frontend uses same-origin `/api/visitors` | N/A | No | No | No | No |
| CFG-030 | PUBLIC_API_PATH | Frontend | none currently | path | No | — | Not consumed by current frontend source; API path is frozen by VC-001 | **Do not introduce as runtime configuration**; canonical path is `/api/visitors` | N/A | No | No | No | No |
| CFG-031 | API_VERSION | Frontend/backend | none currently | string | No | — | No approved consumer | **Do not introduce**; VC-001 is the authoritative interface | N/A | No | No | No | No |

## OIDC identifier classification

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` are non-secret OIDC identifiers. They are supplied as protected GitHub production environment variables and are not GitHub Secrets. No long-lived Azure credential is introduced.

## Fixed deployment/runtime settings

- Resource group: `rg-sixteen-resume-prod`.
- Region: East US.
- Frontend Storage: `st16resumeweb`.
- Function Storage: `st16resumefunc`.
- Deployment Storage: `st16resumedeploy`.
- Deployment container: `function-deployments`.
- Function plan: `sixteen-resume-functions`.
- Function App: `func-sixteen-resume`.
- Cosmos account: `cosmos-sixteen-resume`.
- Cosmos table: `VisitorCounter`.
- Function runtime: Linux Flex Consumption FC1, Python 3.12, Functions v4, scale-to-zero, zero always-ready, 512 MB instance memory, maximum one active instance.
- Public API: `GET /api/visitors`; no browser credential.
- Frontend API request: same-origin `/api/visitors`; no separately configured API base URL is approved.

## Configuration rules

1. Unknown or unprovisioned values are **TBD/PENDING PROVISIONING**, never guessed.
2. Production configuration cannot use local/test values.
3. Browser configuration contains no Azure/Cosmos credentials.
4. ARM remains the source of truth for Azure resource configuration.
5. GitHub production environment configuration is the source of CI/CD deployment inputs that are intentionally external to the repository.


## Controlled live verification correction — 2026-10-07

- Frontend UAMI `sixteen-resume-frontend-github` has now been provisioned in `rg-sixteen-resume-prod` with client ID `2d19e037-cc57-462c-a950-862f9b8a80e6` and principal ID `200b60d9-b05a-4733-81f4-1053834de5c3`.
- Its production federated credential was corrected to subject `repo:s1xte3n/sixteen-resume-frontend:environment:production` and audience `api://AzureADTokenExchange`.
- GitHub frontend `AZURE_FRONTEND_IDENTITY_NAME` has been configured. The protected frontend `AZURE_CLIENT_ID` must be synchronized to the new UAMI client ID before verification can pass.
- Storage Blob Data Contributor on `st16resumeweb` remains unverified because local Azure CLI role-assignment operations return `MissingSubscription` despite a valid subscription context.
- No client secret, Storage key, SAS token, Cosmos key, or alternate authentication mechanism is authorized.
