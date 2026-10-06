# Backend CI/CD Evidence

## Phase 2 status

**BLOCKED — Flex implementation is present; live Azure deployment and runtime evidence cannot be independently verified from source inspection.**

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
