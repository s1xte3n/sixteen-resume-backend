# Backend CI/CD Evidence

## Phase 2 status

**CONDITIONAL — local/CI validation passes; authenticated Azure deployment and runtime evidence remain pending.**

## Phase 3 current blocker — 2026-10-07

The production OIDC federation was corrected and the workflow progressed beyond the previous `AADSTS70025` failure. Azure ARM validation then failed on the role-assignment resource names because the template used `reference()` inside a resource `name` expression. ARM rejects `reference()` at that location.

The corrective implementation makes role-assignment names deterministic from resource IDs, the Function App name, and stable role identifiers. The managed-identity `reference()` remains only in the role-assignment `principalId` properties. This preserves the approved identity/RBAC model without broadening permissions or changing the API contract.

The deployment Blob service dependency was also corrected to include the required `default` blob-service name.

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
- Required production variables are configured and non-empty.
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

## Phase 4 continuation — 2026-10-07

### ARM validation evidence

The current main ARM template was validated directly against Azure with:

- resource group: rg-sixteen-resume-prod
- location: eastus
- deployment storage account: st16resumedeploy
- deployment storage container: function-deployments
- Function plan: sixteen-resume-functions
- Function App: func-sixteen-resume
- Cosmos account: cosmos-sixteen-resume
- Cosmos table: VisitorCounter
- CORS origin: https://sixteen-resume.mooo.com

Azure returned `provisioningState: Succeeded`.

This closes the previously active ARM template validation defects. It does **not** prove ARM deployment, package deployment, runtime startup, API behavior, or production cost.

### OIDC evidence

The production Entra federated credential currently has:

- issuer: https://token.actions.githubusercontent.com
- audience: api://AzureADTokenExchange
- subject: repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production

The subsequent GitHub Actions login returned:

`No subscriptions found for ***.`

Therefore the production deployment identity has not yet demonstrated access to the approved Azure subscription.

### Deployment-storage parameter failure

A subsequent validation attempt supplied:

`deploymentStorageAccountName=""`

Azure correctly rejected the request because the ARM parameter has a minimum length of three characters.

This does **not** require another ARM template change.

The approved production invocation must supply:

- `deploymentStorageAccountName=st16resumedeploy`
- `deploymentStorageContainerName=function-deployments`

The workflow already passes both GitHub environment variables. The production GitHub environment therefore needs those variables populated with the approved values.

### Remaining Phase 4 blocker

**BLOCKED — production GitHub environment configuration and deployment identity authorization.**

Manual repair of production infrastructure is not authorized. Do not add Owner or Contributor merely to bypass the OIDC failure, and do not add a client secret or publish profile.

After the production variables are corrected and the deployment identity has the approved least-privilege permissions, run the protected main workflow and capture the complete Azure execution evidence.

Until that succeeds, ARM deployment, package deployment, runtime startup, API regression, persistence/concurrency, browser/Cosmos isolation, CORS, security, observability, and cost remain unproven.

### Evidence boundary

The direct `az deployment group validate` result is valid ARM validation evidence, but it is not a substitute for the required GitHub OIDC production execution evidence.
