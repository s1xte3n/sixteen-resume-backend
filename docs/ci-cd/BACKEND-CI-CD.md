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
