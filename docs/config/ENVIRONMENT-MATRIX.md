# Phase 5 — Environment Matrix

## Deployment model

There is exactly **one Azure deployment environment: production**. Local, test, CI, and deployment are execution contexts, not additional Azure environments.

| Configuration class | Local | Automated test | CI validation | Deployment | Production |
|---|---|---|---|---|---|
| Azure deployment | No | No | No | Targets production | Yes |
| APP_ENV | local | test/local as required | test/CI | production | production |
| Azure region | N/A | N/A | Validation input only | eastus | eastus |
| Resource group | N/A | N/A | Optional validation input | required | rg-sixteen-resume-prod |
| Frontend Storage | N/A | Mock/local only | Structural validation | ARM output/input | st16resumeweb |
| Function Storage | Azurite if used | Azurite | No live dependency | ARM | st16resumefunc |
| Deployment Storage | N/A | N/A | Template validation | ARM | st16resumedeploy |
| Cosmos Table | Synthetic/Azurite | Synthetic/Azurite | No production data | ARM | VisitorCounter |
| Cosmos credentials | None | None | None | None | None |
| Function identity | Developer/local credentials only if explicitly needed | None | GitHub OIDC for deployment only | GitHub OIDC | System-assigned managed identity |
| Backend OIDC | No | No | No deployment | Required | GitHub production environment |
| Frontend OIDC | No | No | No deployment | Required | GitHub production environment |
| CORS origin | Local/test origin only when needed | Synthetic/test origin | Validated if supplied | Required | **TBD until final approved public origin** |
| Public hostname | No | No | No | Required when edge is provisioned | **TBD** |
| HTTPS edge | No | No | No | Not yet approved | **TBD/configuration gate** |
| VERIFY_PUBLIC_ENDPOINT | false/not used | false | false | false until edge exists | false until edge acceptance; then true |
| Test counter state | synthetic | isolated | isolated | none | production counter only |
| Logs | local stderr | CI logs | CI logs | deployment evidence | Azure platform/application logs |
| Real visitor data | forbidden | forbidden | forbidden | forbidden | approved counter only |

## Context rules

### Local
Use `local.settings.json` derived from the committed example. Azurite is the approved local Table API emulator. Any local secret-bearing file is untracked.

### Automated test
Use synthetic state. `RUN_AZURITE_TESTS=true` enables persistence/concurrency integration tests. Tests must not use production Cosmos credentials or production entities.

### CI
Backend CI runs Python tests, ARM structure tests, Azurite persistence tests, and local HTTP contract tests. Frontend CI validates static artifacts. CI must not require production data.

### Deployment
GitHub Actions uses Microsoft Entra OIDC. No client secret, publish profile, SAS token, Cosmos key, or Storage connection string is required.

### Production
Azure resources are provisioned by ARM. Function runtime accesses Cosmos Table through its system-assigned managed identity. The browser receives only public HTTP responses.

## Environment invariants

The following must not vary by environment in a way that changes approved behavior:

- API method/path: GET /api/visitors.
- Browser-to-Cosmos isolation.
- Managed identity model for production runtime.
- OIDC model for production CI/CD.
- Production data model: VisitorCounter/Global.
- No authentication for public counter API.

Only configuration appropriate to the execution context may vary.
