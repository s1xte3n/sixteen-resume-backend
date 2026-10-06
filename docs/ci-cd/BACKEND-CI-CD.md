# Backend CI/CD

## Status

**Flex Consumption deployment workflow implemented; current production gate is blocked on ARM template validation and authenticated Azure deployment evidence.**

## Pipeline

- Pull requests to main/develop: validation only.
- Pushes to main: validation, then protected production deployment.
- Validation installs Python 3.12 dependencies, runs unit/persistence/ARM/HTTP contract tests, and starts the local Azure Functions host.
- Production authenticates through GitHub Actions Microsoft Entra OIDC.
- The workflow verifies current Flex Consumption regional availability and Python 3.12 availability before deployment.
- ARM is validated and deployed through infra/azure/azuredeploy.json.
- The deployed plan is verified as FC1 / FlexConsumption.
- The Function App is verified as Linux, system-assigned identity, Python 3.12, Functions v4, zero always-ready, required Flex instance memory, maximum instance count 1, and identity-based runtime storage.
- The workflow builds a ready-to-run released-package.zip.
- Azure/functions-action@v1 performs the supported Flex package deployment path; the workflow does not directly upload a package into the deployment container.
- The Function App state is verified after package deployment.
- Deployment evidence is uploaded as a GitHub Actions artifact.
- Any test, ARM, authentication, package, or deployment failure fails the workflow.

## Production environment

GitHub environment: production

### OIDC secrets

AZURE_CLIENT_ID  
AZURE_TENANT_ID  
AZURE_SUBSCRIPTION_ID

These are OIDC identifiers. No client secret, publish profile, storage key, SAS token, or Azure connection string is used.

### Variables

AZURE_RESOURCE_GROUP  
AZURE_LOCATION  
FRONTEND_STORAGE_ACCOUNT_NAME  
FUNCTION_STORAGE_ACCOUNT_NAME  
DEPLOYMENT_STORAGE_ACCOUNT_NAME  
DEPLOYMENT_STORAGE_CONTAINER_NAME  
FUNCTION_PLAN_NAME  
FUNCTION_APP_NAME  
COSMOS_ACCOUNT_NAME  
COSMOS_TABLE_NAME  
CORS_ALLOWED_ORIGIN

Configure these as production environment variables. Do not commit environment-specific secret values.

## Flex deployment storage

The Function App uses a private Blob container as its deployment source through functionAppConfig.deployment.storage.

Authentication is SystemAssignedIdentity.

The deployment storage account is separate from runtime host storage so deployment access can use Storage Blob Data Contributor without expanding the deployment identity's scope beyond package access.

## Runtime storage

The Function App uses:

AzureWebJobsStorage__accountName

No AzureWebJobsStorage connection string is configured in production.

The runtime Storage account disables shared-key access.

The Function App system-assigned identity receives the documented host-storage roles.

## Package deployment

Flex Consumption uses package deployment.

The workflow creates a ready-to-run released-package.zip containing the Function entry point, host configuration, source package, and installed Python dependencies.

Direct Blob upload to the deployment container is not used as the activation mechanism.

## Evidence

Production deployment produces:

- arm-deployment.json
- flex-locations.json
- flex-python-runtimes.json
- flex-plan.json
- flex-app.json
- function-settings.json
- deployment-evidence.txt
- released-package.zip

The evidence records the commit, workflow run, resource group, Function App, hosting plan, ARM outcome, and package deployment model.

## Current production blocker

The production deployment workflow reached Azure after OIDC federation was corrected, but Azure ARM validation currently fails because the ARM template used `reference()` inside role-assignment resource names. ARM does not permit `reference()` at that location.

The corrective change makes every role-assignment resource name deterministic from resource identity and stable deployment inputs, while retaining `reference()` only in the role-assignment `principalId` property, where the Function App system-assigned identity is required. The Cosmos Table role-assignment name follows the same deterministic pattern.

The workflow already passes `DEPLOYMENT_STORAGE_ACCOUNT_NAME` and `DEPLOYMENT_STORAGE_CONTAINER_NAME`; empty deployment-storage values must not be used for production validation.

## Remaining verification

Source inspection cannot prove:

1. Production GitHub environment configuration.
2. Azure federated OIDC credential.
3. Deployment identity RBAC.
4. Subscription-specific East US Flex capacity.
5. Successful ARM deployment.
6. Successful Flex package deployment.
7. Function runtime startup.
8. Runtime Storage RBAC.
9. Cosmos Table RBAC.
10. Production API regression without violating the approved visitor semantics.
11. Production cost <= R100/month.
12. Public HTTPS/CDN and hostname acceptance.

No pending item is represented as passed.

## Architecture boundary

The workflow deploys only the approved core ARM infrastructure and Function application. It does not select or modify the unresolved HTTPS/CDN edge service.

Y1/Linux Consumption is historical/superseded and is not a deployment option.

The API remains GET /api/visitors and hosting migration does not authorize contract changes.

The approved recurring Azure/cloud cost ceiling remains R100/month, with R0/month preferred.

## Phase 4 continuation — 2026-10-07

The ARM template validation defects identified during Phase 3 have been corrected and independently validated against Azure. The deployment workflow remains gated on a successful production GitHub Actions OIDC execution and least-privilege deployment authorization.

**Current production gate: BLOCKED.**

No API, hosting baseline, deployment model, or credential model has been changed. Y1/Linux Consumption, client secrets, publish profiles, and broad permission escalation remain prohibited.


## Phase 4 continuation — RBAC deployment prerequisite — 2026-10-07

The ARM template validation defects are resolved. Direct Azure validation now returns `provisioningState: Succeeded` for the approved production parameters.

The active blocker is now narrower: the GitHub Actions deployment service principal (object ID `8d9ee8de-bc32-4744-b44a-616cafd83559`) can authenticate through the approved OIDC federation but does not have `Microsoft.Authorization/roleAssignments/write` at the production resource-group scope. The ARM template intentionally creates the Function identity's Storage/Cosmos RBAC assignments, so the deployment identity must have constrained role-assignment-management permission.

Required manual Azure prerequisite:

- Do not grant Owner.
- Do not grant Contributor.
- Do not add a client secret or publish profile.
- Grant the deployment identity the least-privileged role-assignment capability required by the ARM deployment, preferably Role Based Access Control Administrator with an ABAC condition restricted to the three approved data roles used by the template: Storage Blob Data Owner, Storage Table Data Contributor, and Storage Blob Data Contributor, and ServicePrincipal principals.
- Scope that delegation to `/subscriptions/aab5f649-b686-4f86-95cc-aa72ae71f03b/resourceGroups/rg-sixteen-resume-prod` only.

After the prerequisite is applied, the only authorized production test is a fresh GitHub Actions run from `main`. No manual production ARM deployment is an acceptable substitute for CI evidence.

**Phase 4 remains BLOCKED until that workflow succeeds and produces the required deployment/runtime evidence.**

## Phase 4 continuation — FC1 instance memory requirement — 2026-10-07

The first controlled production ARM deployment reached the Function App resource and Azure rejected `functionAppConfig.scaleAndConcurrency.instanceMemoryMB` because Flex requires an explicit instance memory value. Azure reported the supported values as `512`, `2048`, and `4096` MB.

The approved template is corrected to set `instanceMemoryMB` explicitly to **512 MB**, the lowest Azure-supported value and the value consistent with the project's low-cost serverless visitor-counter workload. This is an Azure provider-required configuration value; it does not introduce an invented capacity target.

`alwaysReady` remains an empty array, so zero always-ready instances and scale-to-zero remain unchanged. No maximum instance count, HTTP concurrency, or site-update strategy has been added.

The ARM structural test now asserts the required `instanceMemoryMB: 512` value. This correction does not change the API, storage model, Cosmos model, identity model, RBAC scopes, or deployment architecture.

**Current gate: BLOCKED.** The corrected branch must pass CI and the production workflow must be rerun from `main`. The failed deployment must not be manually repaired.
