# Backend CI/CD Evidence

## Phase 2 status

**CONDITIONAL — local/CI validation passes; authenticated Azure deployment and runtime evidence remain pending.**

## Phase 3 current blocker — 2026-10-07

The production OIDC federation was corrected and the workflow progressed beyond the previous `AADSTS70025` failure. Azure ARM validation then failed on the role-assignment resource names because the template used `reference()` inside a resource `name` expression. ARM rejects `reference()` at that location.

The corrective implementation makes role-assignment names deterministic from resource IDs, the Function App name, and stable role identifiers. The managed-identity `reference()` remains only in the role-assignment `principalId` properties. This preserves the approved identity/RBAC model without broadening permissions or changing the API contract.

Production deployment remains **BLOCKED** until the corrected template passes Azure `az deployment group validate` and the subsequent controlled production run proves ARM deployment and runtime behavior.



## Implemented

- Python 3.12 validation.
- Python unit tests.
- ARM structural validation for Flex.
- Azurite persistence and concurrency tests.
- Local Function HTTP contract tests.
- Azure OIDC authentication.
- Flex regional availability validation.
- Python 3.12 Flex runtime availability validation.
- Azure ARM validation.
- Azure ARM deployment.
- Deployed FC1/Linux/functionAppConfig verification.
- Identity-based runtime storage verification.
- Private deployment-container verification.
- Ready-to-run Function package creation.
- Flex-compatible package deployment through Azure/functions-action.
- Post-deployment Function App state verification.
- Deployment evidence artifact upload.
- Production deployment isolation through the production environment.
- No Azure credentials committed to source.

## Live verification state

The production workflow defines the required deployment sequence, but source inspection is not proof that the sequence has succeeded against Azure.

The following remain **BLOCKED** pending authenticated production evidence:

- Production GitHub environment exists.
- Required OIDC identifiers are configured.
- Required production variables are configured.
- Azure federated credential exists and matches the GitHub OIDC subject/audience.
- Deployment identity has approved permissions.
- East US Flex capacity is available for the actual subscription.
- Controlled main deployment run succeeds.
- ARM provisioning state is Succeeded.
- Deployed plan is FC1 / FlexConsumption.
- Function App is Linux with system-assigned identity.
- Function runtime is Python 3.12 / Functions v4.
- Runtime storage uses identity-based configuration.
- Deployment storage is private and identity-authenticated.
- Function package deployment succeeds.
- Function App reaches Running state.
- Runtime identity can access Cosmos Table API.
- Production recurring cost is <= R100/month.
- Public HTTPS/CDN and hostname acceptance is complete.

## Evidence rule

A workflow definition is not deployment evidence.

A test is not passed merely because the command exits successfully.

Azure acceptance requires authenticated evidence for:

Requirement -> IaC -> Azure resource -> identity/RBAC -> deployment -> runtime -> API -> cost -> release.

See infra/azure/VALIDATION.md for the complete Flex validation boundary.


## CI evidence — 2026-10-06

Backend CI run 51 completed successfully for commit 17c31e72e130056fe1419988dab8aff4b92173f0.

Validation evidence included:

- Python dependency installation.
- deterministic unit tests: passed.
- Flex ARM structural tests: passed.
- Azurite persistence/concurrency tests: passed.
- Azure Functions Core Tools installation: passed.
- local Functions host startup: passed.
- executable GET /api/visitors HTTP contract tests: passed.

Backend Tests run 51 also completed successfully.

This CI result does not prove authenticated Azure provisioning, subscription-specific Flex capacity, production RBAC, production package deployment, production runtime behavior, or production cost compliance.

### 2026-10-07 ARM validation correction — deployment Blob service resource ID

Azure validation advanced past the role-assignment naming defect but then failed because the deployment Blob service dependsOn used resourceId('Microsoft.Storage/storageAccounts/blobServices', accountName) without the required default blob-service resource name. The correction changes this dependency to resourceId('Microsoft.Storage/storageAccounts/blobServices', accountName, 'default').

This is a template-reference correction only. It does not change the deployment Storage account, private container, managed-identity authentication, RBAC scope, Function App configuration, or API contract. Production remains BLOCKED until the corrected template passes Azure validation and subsequent deployment evidence is observed.

## Phase 4 continuation — 2026-10-07

### Current evidence

The current main ARM template was validated directly against Azure with the approved production parameters. Azure returned provisioningState: Succeeded for deployment validation in rg-sixteen-resume-prod / eastus. This supersedes the earlier ARM-template validation defects as active blockers.

The production Entra federated identity credential was also recreated with:

- issuer: https://token.actions.githubusercontent.com;
- audience: api://AzureADTokenExchange;
- subject: repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production.

The subsequent GitHub Actions OIDC login still failed with No subscriptions found. Therefore the identity has not yet demonstrated access to the approved subscription through the production workflow.

### Remaining Phase 4 blocker

**BLOCKED — deployment identity authorization.** The deployment service principal must receive only the approved deployment permissions at the approved scope. The previous role-assignment attempts failed because the subscription ID used in the command was malformed/mismatched. Do not compensate with Owner, a client secret, a publish profile, or manual production deployment.

After the exact subscription scope and least-privilege role assignment are corrected, run the production workflow from main and capture the complete Azure execution evidence. Until then, ARM deployment, package deployment, runtime, API, persistence/concurrency, isolation, CORS, security, and cost remain unproven.

### Evidence boundary

The direct az deployment group validate result is valid ARM validation evidence, but it is not a substitute for the required GitHub OIDC production execution evidence.
