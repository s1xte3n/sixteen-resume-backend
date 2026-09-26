# Backend CI/CD Evidence

## Phase 7 status

**BLOCKED — implementation is present; live Azure deployment and runtime evidence cannot be independently verified from the current environment.**

## Implemented

- Backend dependency installation.
- Python unit tests.
- ARM structural validation.
- Azurite persistence tests.
- Local Function HTTP contract tests.
- Azure OIDC authentication.
- Azure ARM validation.
- Azure ARM deployment.
- Function package creation.
- Function App deployment.
- Deployment evidence artifact upload.
- Production deployment isolation through the `production` environment.
- No Azure credentials committed to source.

## Live verification state

The production workflow is present and defines the required deployment sequence, but source inspection is not proof that the sequence has succeeded against Azure.

The following remain **BLOCKED** pending authenticated production evidence:

- Production GitHub environment exists.
- Required OIDC secrets are configured.
- Required production variables are configured.
- Azure federated credential exists.
- Deployment identity has approved permissions.
- Controlled `main` deployment run succeeds.
- ARM provisioning state is `Succeeded`.
- Function package deployment succeeds.
- Retained deployment artifacts are available.
- Each provisioned Azure resource can be independently enumerated and verified.
- Function application settings and CORS are confirmed effective.
- Production logging/telemetry is confirmed.
- Public HTTPS endpoint is reachable.
- Visitor-counter API contract succeeds against production.
- Cosmos persistence is verified before/after the approved synthetic calls.
- Expected error behavior is verified.
- Frontend displays the resulting persisted count.

See `docs/ci-cd/PHASE-7-LIVE-AZURE-DEPLOYMENT-VERIFICATION.md` for the complete evidence matrix.

No pending item is represented as passed.
