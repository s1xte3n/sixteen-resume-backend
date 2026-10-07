# Phase 2 — Azure Functions Flex Consumption IaC Validation

## Status
**Implementation complete; authenticated Azure validation currently BLOCKED by an ARM role-assignment naming defect; correction prepared on the implementation branch.**

Y1/Linux Consumption is historical evidence only. No Y1 quota increase is required or authorized.

## Current hosting baseline

| Property | Approved/current |
|---|---|
| Hosting | Azure Functions Flex Consumption |
| SKU | FC1 |
| OS | Linux |
| Functions runtime | v4 |
| Python | 3.12 |
| Scaling | Serverless scale-to-zero |
| Always-ready | Zero for MVP |
| Function identity | System-assigned managed identity |
| Runtime storage | Identity-based AzureWebJobsStorage__accountName |
| Deployment source | Private Blob container |
| Deployment auth | System-assigned managed identity |
| Package deployment | Flex-compatible package deployment through supported tooling |
| Persistence | Azure Cosmos DB Table API |
| Cosmos capacity | Serverless |
| IaC | ARM |
| CI/CD | GitHub Actions |
| Azure authentication | Microsoft Entra OIDC |
| Region | East US |

## Structural validation

`tests/test_arm_template.py` verifies:
- East US is the only allowed deployment region.
- The Functions plan is FC1 / FlexConsumption.
- Linux is represented by the Function App resource kind.
- functionAppConfig contains Flex deployment storage, runtime and scale configuration.
- Python 3.12 is configured in functionAppConfig.runtime.
- alwaysReady is explicitly empty for the MVP.
- Instance memory is explicitly set to 512 MB because Flex requires it; maximum instance count is explicitly set to 1 because Azure requires a value and the project selects the lowest active-instance ceiling consistent with the low-cost MVP. HTTP concurrency and site-update strategy are not invented as fixed values.
- Deployment storage is a private blob container.
- Deployment storage uses system-assigned managed-identity authentication.
- Runtime storage uses AzureWebJobsStorage__accountName.
- Legacy WEBSITE_CONTENTAZUREFILECONNECTIONSTRING, WEBSITE_CONTENTSHARE, and WEBSITE_RUN_FROM_PACKAGE settings are absent.
- Runtime/deployment storage accounts disable shared-key access.
- Function system-assigned identity is present.
- Runtime storage RBAC uses Storage Blob Data Owner plus Storage Table Data Contributor.
- Deployment storage RBAC uses Storage Blob Data Contributor.
- Cosmos Table RBAC remains scoped to VisitorCounter.
- Cosmos Table API serverless capability remains enabled.
- No long-lived credential markers are present.
- No Y1/Dynamic hosting configuration remains.

## Package/deployment validation

The backend CI workflow:
1. Runs Python unit tests.
2. Runs persistence tests.
3. Runs ARM structural tests.
4. Runs local HTTP contract tests for GET /api/visitors.
5. Authenticates to Azure through OIDC on main.
6. Verifies current Flex Consumption regional availability.
7. Verifies Python 3.12 is listed for Flex in the approved region.
8. Runs az deployment group validate.
9. Deploys the ARM template.
10. Verifies ARM provisioning state.
11. Verifies the deployed FC1/Linux/Python 3.12/functionAppConfig/runtime-storage configuration.
12. Builds a ready-to-run released-package.zip.
13. Deploys the package through Azure/functions-action@v1 using the supported Flex package-deployment path.
14. Verifies the Function App reaches Running.
15. Uploads deployment evidence.

Direct upload of a package into the deployment container is not used as a deployment mechanism.

## Identity/RBAC validation

### Function runtime identity
The Function App uses a system-assigned managed identity.

It is authorized for:
- runtime host storage on the runtime Storage account;
- Cosmos DB Table API access scoped to the VisitorCounter table;
- deployment package access on the private deployment Storage account.

### Storage roles

| Scope | Role | Purpose |
|---|---|---|
| Runtime Storage account | Storage Blob Data Owner | Minimum documented host-storage permission |
| Runtime Storage account | Storage Table Data Contributor | Host diagnostic table operations |
| Deployment Storage account | Storage Blob Data Contributor | Deployment package access |

No Storage keys or SAS tokens are configured for the Function App.

## Local validation

pytest -q tests/test_arm_template.py
pytest -q tests/test_visitors.py
RUN_AZURITE_TESTS=true pytest -q tests/test_table_counter.py
RUN_FUNCTION_HOST_TESTS=true FUNCTION_BASE_URL=http://127.0.0.1:7071 pytest -q tests/test_http_contract.py

These prove source and local behavior only. They do not prove Azure provisioning, RBAC, Flex capacity, package deployment, or production runtime behavior.

## Authenticated Azure validation

Required commands:

az functionapp list-flexconsumption-locations --query "sort_by(@, &name)[].{Region:name}" -o table
az functionapp list-flexconsumption-runtimes --location eastus --runtime python -o json
az deployment group validate with infra/azure/azuredeploy.json and the production resource-group parameters.

The Flex availability command proves that East US is currently listed as a supported Flex region; it does not prove subscription-specific capacity.

Subscription-specific capacity is validated only by a successful authenticated ARM deployment.

## Live evidence still required

1. East US Flex capacity for the actual subscription.
2. Successful ARM deployment.
3. Function managed identity access to runtime storage.
4. Function managed identity access to deployment storage.
5. Cosmos Table RBAC authorization.
6. Successful Flex package deployment.
7. Function runtime startup.
8. API regression against the deployed Function.
9. GitHub OIDC federation and RBAC execution.
10. Production cost evidence <= R100/month.
11. HTTPS/CDN and public hostname evidence.
12. End-to-end frontend counter verification.

## Failure classification

| Failure | Expected gate behavior |
|---|---|
| East US not listed for Flex | Deployment blocked |
| Python 3.12 unavailable in East US Flex | Deployment blocked |
| Subscription lacks Flex capacity | Deployment blocked |
| ARM validation fails | CI fails before deployment |
| ARM deployment fails | CI fails |
| Function package deployment fails | CI fails |
| Function App not Running after package deployment | CI fails |
| OIDC authentication fails | CI fails |
| Storage RBAC missing | Deployment/runtime verification fails |
| Cosmos RBAC missing | API/runtime verification fails |
| Cost exceeds R100/month | Production blocked |
| Y1/Dynamic plan appears | Immediate release blocker |

## API contract

The API contract remains unchanged: GET /api/visitors.

Flex migration does not change the method, path, response schema, error schema, request-ID behavior, visitor semantics, persistence semantics, concurrency semantics, CORS boundary, or browser-to-Cosmos isolation.

## Security boundary

No browser-facing component receives Storage keys, SAS tokens, Cosmos credentials, Azure deployment credentials, or client secrets.

GitHub Actions uses Microsoft Entra OIDC.

## Acceptance boundary

Phase 2 infrastructure is implementation-complete when the repository contains the Flex architecture and local structural tests pass.

Phase 2 is production-ready only after authenticated Azure validation, deployment evidence, runtime/RBAC verification, CI/CD evidence, and cost validation pass.

## Executed CI evidence

Backend CI run 51 for the Phase 2 branch completed successfully on 2026-10-06. The run passed deterministic unit tests, Flex ARM structural tests, Azurite persistence/concurrency tests, local Functions host startup, and executable HTTP contract tests.

Authenticated Azure validation was not executed by the PR workflow because production deployment is intentionally gated to a push to main. Therefore Azure provisioning, Flex subscription capacity, OIDC production execution, runtime RBAC, package activation, and cost validation remain unproven.


## Phase 3 — Authenticated Azure Deployment Verification

**Gate status: BLOCKED.**

### 2026-10-07 validation blocker and correction

Azure `az deployment group validate` reached template evaluation and rejected the role-assignment resource names because they used `reference()` to obtain the Function App managed-identity principal ID inside the resource `name` expression. ARM does not permit `reference()` at that location.

The correction is intentionally limited to resource-name determinism:

- Storage role-assignment names use `guid(resourceId(...), parameters('functionAppName'), roleDefinitionIdVariable)`.
- The Cosmos Table role-assignment name uses `guid(resourceId(...table...), parameters('functionAppName'), stableRoleKey)`.
- `reference(...).identity.principalId` remains in the `properties.principalId` fields, where the Function App identity is consumed.
- No role scope, role definition, Function App identity model, deployment storage model, or API contract is changed.

The workflow must be revalidated against Azure after this correction. No production deployment evidence may be marked PASS from source inspection alone.


Executed evidence on 2026-10-06 against backend main commit 53035b2d1d81d431a29180738e3a9c77f2081e23:

- GitHub Actions run: 37520785334 (Backend CI, run 54).
- Validation job passed.
- Deployment job reached azure/login@v3 and requested GitHub OIDC authentication.
- Azure rejected the token with AADSTS70025: the deployment application had no configured federated identity credentials.
- OIDC token evidence observed by Azure login: issuer https://token.actions.githubusercontent.com; audience api://AzureADTokenExchange; production environment subject emitted by GitHub; workflow reference .github/workflows/backend-ci.yml@refs/heads/main.
- ARM validation did not execute because OIDC authentication failed first.
- ARM deployment did not execute.
- Flex regional availability was not proven by this production run.
- Subscription-specific Flex capacity was not proven.
- Deployed Function configuration, runtime storage, deployment storage, RBAC, Cosmos authorization, package activation, runtime startup, API regression, persistence, concurrency, CORS, cost, and production observability were not proven.

No manual Azure repair, client secret, publish profile, or alternate authentication mechanism was used.

The failure is a release blocker and must be resolved by provisioning the approved federated identity credential for the production GitHub environment, followed by a fresh authenticated workflow run. The exact issuer, subject, audience, tenant, subscription, identity and RBAC must then be re-verified from live execution evidence.

The previously recorded Phase 2 CI evidence remains valid for source/local validation only. It must not be interpreted as production deployment evidence.

### 2026-10-07 ARM validation correction — deployment Blob service resource ID

Azure validation advanced past the role-assignment naming defect but then failed because the deployment Blob service dependsOn used resourceId('Microsoft.Storage/storageAccounts/blobServices', accountName) without the required default blob-service resource name. The correction changes this dependency to resourceId('Microsoft.Storage/storageAccounts/blobServices', accountName, 'default').

This is a template-reference correction only. It does not change the deployment Storage account, private container, managed-identity authentication, RBAC scope, Function App configuration, or API contract. Production remains BLOCKED until the corrected template passes Azure validation and subsequent deployment evidence is observed.

## Phase 4 continuation — 2026-10-07

### ARM validation correction verified

Authenticated Azure CLI validation of the current main ARM template completed with provisioningState: Succeeded against rg-sixteen-resume-prod in eastus using the approved production parameters, including the dedicated deployment Storage account/container. The two template defects previously observed are therefore corrected:

- role-assignment resource names no longer depend on reference();
- the deployment Blob service dependency uses the required default child resource name.

This validates template evaluation only. It does not prove GitHub OIDC execution, ARM deployment, Flex subscription capacity, runtime startup, package activation, API regression, persistence/concurrency, CORS, security, or cost.

### OIDC/RBAC state

The production federated credential now exists with the approved GitHub Actions issuer and api://AzureADTokenExchange audience and the production repository/environment subject. A GitHub Actions OIDC login has nevertheless not yet produced an authenticated Azure subscription context; the observed workflow failure was No subscriptions found. Deployment-identity RBAC must be corrected and then re-tested through the production workflow. No client secret, publish profile, or broad Owner/Contributor bypass is authorized.

### Gate

**Phase 4: BLOCKED.** A fresh successful production GitHub Actions execution remains mandatory before any production deployment or runtime verification can be marked passed.


## Phase 4 continuation — RBAC prerequisite — 2026-10-07

### Verified

The current `infra/azure/azuredeploy.json` passes Azure deployment-group template validation against the approved production resource group and parameters. The earlier `reference()` resource-name defect and Blob service `resourceId()` defect are therefore resolved.

### Active blocker

The production GitHub Actions identity is now reaching ARM but Azure rejects the role-assignment resources because the deployment identity lacks:

`Microsoft.Authorization/roleAssignments/write`

Deployment identity object ID:

`8d9ee8de-bc32-4744-b44a-616cafd83559`

Approved resource-group scope:

`/subscriptions/aab5f649-b686-4f86-95cc-aa72ae71f03b/resourceGroups/rg-sixteen-resume-prod`

The ARM template must retain its managed-identity RBAC resources. Removing them or pre-provisioning them manually would weaken the IaC authority model and is not an approved workaround.

### Manual prerequisite

Use a narrowly constrained role-assignment delegation for the deployment service principal. Preferred built-in role: **Role Based Access Control Administrator**, scoped to the production resource group and conditioned so role-assignment writes/deletes are limited to the three approved role definition IDs already used by the template:

- Storage Blob Data Owner: `b7e6dc6d-f1e8-4753-8033-0f276bb0955b`;
- Storage Table Data Contributor: `0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3`;
- Storage Blob Data Contributor: `ba92f5b4-2d11-453d-a403-e96b0029c9fe`.

Do not grant Owner or Contributor and do not introduce long-lived credentials.

### Gate

**Phase 4: BLOCKED.** The prerequisite must be applied manually by an authorized Azure administrator, then the production GitHub Actions workflow must be rerun from `main`. Only that fresh execution can establish the required deployment, runtime, API, persistence, security, and cost evidence.

## Phase 4 continuation — FC1 instance memory requirement — 2026-10-07

The first controlled production ARM deployment reached the Function App resource and Azure rejected `functionAppConfig.scaleAndConcurrency.instanceMemoryMB` because Flex requires an explicit instance memory value. Azure reported the supported values as `512`, `2048`, and `4096` MB.

The approved template is corrected to set `instanceMemoryMB` explicitly to **512 MB**, the lowest Azure-supported value and the value consistent with the project's low-cost serverless visitor-counter workload. This is an Azure provider-required configuration value; it does not introduce an invented capacity target.

`alwaysReady` remains an empty array, so zero always-ready instances and scale-to-zero remain unchanged. No HTTP concurrency or site-update strategy has been added. `maximumInstanceCount: 1` is provider-required configuration, not an invented throughput target.

The ARM structural test now asserts the provider-required `instanceMemoryMB: 512` value and `maximumInstanceCount: 1`. This correction does not change the API, storage model, Cosmos model, identity model, RBAC scopes, or deployment architecture.

**Current gate: BLOCKED.** The corrected branch must pass CI and the production workflow must be rerun from `main`. The failed deployment must not be manually repaired.


## Phase 4 continuation — Flex worker runtime setting correction — 2026-10-07

A controlled production deployment reached the Function App resource and Azure rejected the legacy `FUNCTIONS_WORKER_RUNTIME` app setting for Flex Consumption. Flex requires the runtime to be declared through `functionAppConfig.runtime`.

The ARM template therefore removes `FUNCTIONS_WORKER_RUNTIME` from `siteConfig.appSettings`. The existing `functionAppConfig.runtime` remains authoritative as `python` / `3.12`, and `FUNCTIONS_EXTENSION_VERSION=~4` remains unchanged. No hosting SKU, scaling, storage, identity/RBAC, Cosmos, package deployment, API, or CORS behavior is changed.

The ARM structural test now explicitly asserts that `FUNCTIONS_WORKER_RUNTIME` is absent, preventing regression to the rejected Flex configuration.

**Current gate: BLOCKED.** CI must validate the correction, followed by a fresh production GitHub Actions run from `main`. The failed deployment must not be manually repaired.


## Phase 4 continuation — ARM provider corrections — 2026-10-07

The latest controlled deployment exposed two provider-level defects after the earlier ARM validation issues were resolved:

1. **Cosmos Table RBAC API version** — the Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments resource used API version 2023-04-15, which Azure rejected for Table RBAC. It is now pinned to the provider-supported 2026-03-15 API version. The table-scoped role definition and VisitorCounter scope are unchanged.
2. **Frontend static website configuration** — the frontend Storage account attempted to enable static website hosting while allowBlobPublicAccess was false. Azure rejected the static website configuration. The frontend static website account now explicitly permits the anonymous public blob access required by Azure Storage static website hosting. This applies only to the public frontend Storage account; the runtime and private deployment Storage accounts continue to disable shared-key access and private Blob access.

The backend CI verification step was also corrected to require FUNCTIONS_WORKER_RUNTIME to be absent, matching the Flex functionAppConfig.runtime model already enforced by the ARM template.

No API, Cosmos authentication model, managed-identity model, private deployment container, Y1 path, client secret, publish profile, or unrelated frontend implementation was introduced.

**Phase 4 gate: BLOCKED.** These source/IaC corrections require CI and a fresh production GitHub Actions deployment from main before any production PASS can be recorded.


## Phase 4 continuation — Cosmos Table RBAC scope correction — 2026-10-07

The latest controlled ARM deployment reached the Cosmos Table role-assignment resource and Azure rejected the previous `properties.scope` value because the full Table resource ID was not a valid scope for the current Table RBAC provider contract.

The ARM template now uses the Cosmos account resource ID as the role-assignment scope. Microsoft documents this account-level scope for `Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments`; the role definition remains the Cosmos DB for Table data-plane role and its data actions remain table/entity operations. The deployment contains one application table, `VisitorCounter`, so no second application table is introduced by this correction. citeturn4search0turn2search0

This is a provider-contract correction only. No connection string, account key, direct browser access, additional table, API change, or permission broadening was introduced.

**Phase 4 remains BLOCKED** until the corrected template passes authenticated CI/ARM deployment and the live Function identity's Cosmos authorization is directly verified.
