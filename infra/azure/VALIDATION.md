# Phase 2 — Azure Functions Flex Consumption IaC Validation

## Status
**Implementation complete; authenticated Azure validation and production deployment evidence pending.**

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
- Instance memory, maximum instance count, HTTP concurrency and site-update strategy are not invented as fixed values.
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
