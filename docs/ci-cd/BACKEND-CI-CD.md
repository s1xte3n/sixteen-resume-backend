# Backend CI/CD

## Status

**Flex Consumption deployment workflow implemented; current production gate is BLOCKED on production GitHub environment configuration and authenticated Azure deployment evidence.**

## Pipeline

- Pull requests to main/develop: validation only.
- Pushes to main: validation, then protected production deployment.
- Validation installs Python 3.12 dependencies, runs unit/persistence/ARM/HTTP contract tests, and starts the local Azure Functions host.
- Production authenticates through GitHub Actions Microsoft Entra OIDC.
- The workflow verifies current Flex Consumption regional availability and Python 3.12 availability before deployment.
- ARM is validated and deployed through infra/azure/azuredeploy.json.
- The deployed plan is verified as FC1 / FlexConsumption.
- The Function App is verified as Linux, system-assigned identity, Python 3.12, Functions v4, zero always-ready, and identity-based runtime storage.
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

### Required production variables

The backend deployment workflow requires all of the following to be configured in the **production GitHub environment**:

| Variable | Approved value |
|---|---|
| AZURE_RESOURCE_GROUP | rg-sixteen-resume-prod |
| AZURE_LOCATION | eastus |
| FRONTEND_STORAGE_ACCOUNT_NAME | st16resumeweb |
| FUNCTION_STORAGE_ACCOUNT_NAME | st16resumefunc |
| DEPLOYMENT_STORAGE_ACCOUNT_NAME | st16resumedeploy |
| DEPLOYMENT_STORAGE_CONTAINER_NAME | function-deployments |
| FUNCTION_PLAN_NAME | sixteen-resume-functions |
| FUNCTION_APP_NAME | func-sixteen-resume |
| COSMOS_ACCOUNT_NAME | cosmos-sixteen-resume |
| COSMOS_TABLE_NAME | VisitorCounter |
| CORS_ALLOWED_ORIGIN | https://sixteen-resume.mooo.com |

These values must not be empty. In particular, passing an empty `DEPLOYMENT_STORAGE_ACCOUNT_NAME` overrides the ARM parameter's required minimum length and causes `az deployment group validate` to fail before resource validation.

Do not commit environment-specific values to source control. Do not put the OIDC identifiers in source control.

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

The ARM template defects identified during Phase 3 have been corrected.

The current main template was successfully validated directly against Azure using the approved production resource group and non-empty deployment-storage parameters. The validation returned `provisioningState: Succeeded`.

The remaining blocker is the production GitHub environment/OIDC execution path:

1. The Entra federated credential exists with the approved GitHub issuer.
2. The audience is `api://AzureADTokenExchange`.
3. The production repository/environment subject is configured.
4. GitHub Actions reaches Azure OIDC authentication.
5. Azure login still returns `No subscriptions found`, so the deployment identity has not yet demonstrated access to the approved subscription.
6. A separate manual ARM validation attempt failed because `deploymentStorageAccountName=""` was supplied. The ARM template correctly rejects that empty value because the parameter requires at least three characters. This is an invocation/environment-configuration error, not an ARM template defect.

The workflow must be run only with the approved production variables above. Do not use empty deployment-storage values.

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

**Current production gate: BLOCKED.**

ARM structural defects are resolved and direct Azure deployment-group validation has passed. Production release cannot proceed until the GitHub production environment has the approved non-empty deployment variables and the OIDC deployment identity successfully resolves the approved Azure subscription with the required least-privilege permissions.

No API, hosting baseline, deployment model, or credential model has been changed. Y1/Linux Consumption, client secrets, publish profiles, and broad permission escalation remain prohibited.
