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


## Phase 4 continuation — current blocker supersession — 2026-10-07

The previous ARM-template validation blockers are no longer active. Current direct evidence:

- approved production resource group: `rg-sixteen-resume-prod`;
- region: `eastus`;
- ARM validation: **Succeeded**;
- deployment storage account: `st16resumedeploy`;
- deployment container: `function-deployments`;
- federated credential issuer: `https://token.actions.githubusercontent.com`;
- federated credential audience: `api://AzureADTokenExchange`;
- production GitHub subject: `repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`.

The current production failure is:

`Authorization failed ... does not have permission to perform action Microsoft.Authorization/roleAssignments/write`

The affected deployment identity is service principal object ID `8d9ee8de-bc32-4744-b44a-616cafd83559`.

This is a deployment-authority RBAC prerequisite, not an ARM template defect. The approved fix is constrained role-assignment delegation at the production resource-group scope. Owner, Contributor, client secrets, publish profiles, and manual production repair remain prohibited.

The following evidence remains **unproven** until the fresh main workflow succeeds: ARM deployment, Flex subscription capacity, live Function configuration, package activation, runtime startup, Storage/Cosmos authorization, API behavior, persistence/concurrency, browser isolation, CORS, security, observability, and cost.

## Phase 4 continuation — FC1 instance memory requirement — 2026-10-07

The first controlled production ARM deployment reached the Function App resource and Azure rejected `functionAppConfig.scaleAndConcurrency.instanceMemoryMB` because Flex requires an explicit instance memory value. Azure reported the supported values as `512`, `2048`, and `4096` MB.

The approved template is corrected to set `instanceMemoryMB` explicitly to **512 MB**, the lowest Azure-supported value. Azure also requires `maximumInstanceCount` to be explicitly populated; the template sets it to **1**, the lowest permitted value and the smallest active-instance ceiling consistent with the low-cost MVP. These are provider-required configuration values, not invented throughput targets.

`alwaysReady` remains an empty array, so zero always-ready instances and scale-to-zero remain unchanged. No HTTP concurrency or site-update strategy has been added.

The ARM structural test now asserts the required `instanceMemoryMB: 512` value. This correction does not change the API, storage model, Cosmos model, identity model, RBAC scopes, or deployment architecture.

**Current gate: BLOCKED.** The corrected branch must pass CI and the production workflow must be rerun from `main`. The failed deployment must not be manually repaired.


## Phase 4 continuation — Flex worker runtime setting correction — 2026-10-07

### Latest production failure

The controlled production ARM deployment advanced to `Microsoft.Web/sites/func-sixteen-resume` and Azure rejected:

`The following app setting (Site.SiteConfig.AppSettings.FUNCTIONS_WORKER_RUNTIME) for Flex Consumption sites is invalid.`

### Correction

The invalid `FUNCTIONS_WORKER_RUNTIME=python` app setting has been removed from the ARM template. Python 3.12 remains explicitly declared through `functionAppConfig.runtime`, which is the Flex runtime configuration already used by the approved architecture.

The structural test now asserts that `FUNCTIONS_WORKER_RUNTIME` is absent. No alternate credential, manual production repair, hosting-plan change, storage change, API change, or permission broadening was introduced.

### Evidence boundary

This correction is source/IaC evidence only until CI and a fresh production GitHub Actions run from `main` succeed. ARM deployment, package activation, runtime startup, API regression, persistence/concurrency, browser isolation, CORS, security, observability, and cost remain unproven.

**Phase 4 gate: BLOCKED.**


## Phase 4 continuation — ARM provider corrections — 2026-10-07

### Latest controlled deployment findings

The latest production ARM execution advanced beyond the prior RBAC/Function configuration defects but failed on two independent provider validations:

- Cosmos Table role assignment rejected API version 2023-04-15 as too old for RBAC support. The template now uses 2026-03-15.
- Frontend static website configuration rejected the staticWebsite settings while the frontend Storage account had allowBlobPublicAccess=false. The template now enables public Blob access only for the public static website account.

The backend workflow verification was also corrected so the deployed settings must not contain FUNCTIONS_WORKER_RUNTIME; Flex runtime declaration remains solely in functionAppConfig.runtime.

### Evidence boundary

These changes are source/IaC corrections. They do not constitute successful production deployment evidence.

Still unproven until a fresh main production workflow succeeds:

- complete ARM deployment;
- subscription-specific Flex capacity;
- live Function configuration and startup;
- package activation;
- Storage and Cosmos managed-identity authorization;
- API regression;
- persistence and concurrency;
- browser/Cosmos isolation;
- CORS;
- security and observability;
- cost <= R100/month.

**Phase 4 gate: BLOCKED.**


## Phase 4 continuation — Static website API-version correction — 2026-10-07

The controlled production deployment reached the frontend Storage account and Azure rejected the static website request with:

`InvalidRequestParameters: properties.staticWebsiteEnabled`.

Root cause: the ARM template declared `Microsoft.Storage/storageAccounts/blobServices` with API version `2023-05-01`, while the `staticWebsite` deployment property is supported for this resource type beginning with API version `2025-08-01`. The template now uses `2025-08-01` for Blob Service resources, preserving the existing `staticWebsite.enabled=true`, `indexDocument=index.html`, and `errorDocument404Path=404.html` configuration.

The public frontend Storage account continues to use `allowBlobPublicAccess=true`, which is required for Azure Storage static website hosting. Runtime and private deployment Storage accounts remain unchanged and continue to disable shared-key access and public Blob access.

A structural test now locks the frontend Blob Service resource to API version `2025-08-01` so the provider-compatible static website configuration cannot regress to an API version that does not support the property.

No change was made to the Flex Consumption baseline, Function runtime, managed identity, RBAC model, Cosmos Table API, API contract, deployment authentication, or frontend application behavior.

**Phase 4 gate: BLOCKED.** This correction is source/IaC evidence only. CI and a fresh production GitHub Actions deployment from `main` are still required before production deployment or runtime evidence can be marked passed.
