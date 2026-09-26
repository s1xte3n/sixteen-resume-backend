# Backend CI/CD

## Status

**Implemented; production execution pending Azure/GitHub environment configuration and one controlled main-branch run.**

## Pipeline

- Pull requests to `main`/`develop`: validation only.
- Pushes to `main`: validation, then protected production deployment.
- Validation installs Python dependencies, runs unit/persistence/ARM/HTTP contract tests, and starts local Azure Functions.
- Production authenticates through GitHub Actions OIDC.
- ARM is validated and deployed through `infra/azure/azuredeploy.json`.
- The Function application is packaged and deployed after successful ARM deployment.
- Deployment evidence is uploaded as a GitHub Actions artifact.

## Production environment

GitHub environment: `production`

### Secrets

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

These are OIDC identifiers. No client secret, publish profile, storage key, SAS token, or connection string is used.

### Variables

`AZURE_RESOURCE_GROUP`  
`AZURE_LOCATION`  
`FRONTEND_STORAGE_ACCOUNT_NAME`  
`FUNCTION_STORAGE_ACCOUNT_NAME`  
`FUNCTION_PLAN_NAME`  
`FUNCTION_APP_NAME`  
`COSMOS_ACCOUNT_NAME`  
`COSMOS_TABLE_NAME`  
`CORS_ALLOWED_ORIGIN`

Configure these as production environment variables; never commit environment-specific values that are not approved for source control.

## Evidence

Production deployment produces:

- `arm-deployment.json`
- `deployment-evidence.txt`

The evidence records commit, workflow run, resource group, Function App, and ARM deployment outcome.

## Remaining verification

The repository cannot prove the following from source alone:

1. Production GitHub environment configuration.
2. Azure federated OIDC credential.
3. Deployment identity RBAC.
4. Successful Azure deployment.
5. Successful Function deployment.
6. Retained deployment artifact.
7. GitHub main-branch protection/required checks.

The GitHub integration could not read branch-protection configuration, so that item remains **BLOCKED/PENDING VERIFICATION**.

## Architecture boundary

The workflow deploys only the approved core ARM infrastructure and Function application. It does not select the unresolved HTTPS/CDN edge service.

Linux Consumption remains the approved MVP hosting model. Microsoft's announced Linux Consumption retirement on 30 September 2028 is a lifecycle constraint; Flex Consumption migration remains a future requirement.

The approved recurring Azure/cloud cost ceiling remains **R100/month**.
