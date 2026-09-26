# Phase 7 — Live Azure Deployment Verification Evidence

## Verification status

**BLOCKED — live Azure control-plane and production runtime verification could not be executed from the current environment.**

This evidence record deliberately does not infer Azure deployment success from source code, ARM structure, or workflow definitions.

### Blocking dependencies

1. No authenticated Azure control-plane access is available to this verification session.
2. The available GitHub integration can inspect repository source and workflow definitions, but it does not expose an Azure resource-management/session interface for executing `az` commands against the production subscription.
3. The committed deployment workflows require production GitHub environment/OIDC configuration that cannot be independently inspected or executed from the available connector surface.
4. The approved ARM template currently provisions the Azure core resources but intentionally does not provision the unresolved HTTPS/CDN edge service.
5. The frontend JavaScript calls `/api/visitors` on the browser's current origin. A live end-to-end visitor-counter verification therefore requires the approved public edge/routing configuration to make that API path reachable from the deployed frontend.

## Source-controlled implementation evidence

| Item | Source evidence | Live verification |
|---|---|---|
| Resource group | Backend deployment workflow targets `vars.AZURE_RESOURCE_GROUP` | **BLOCKED** |
| Frontend Storage account | ARM resource `Microsoft.Storage/storageAccounts` + static website child resource | **BLOCKED** |
| Static website | ARM `staticWebsite.enabled=true`, index `index.html` | **BLOCKED** |
| Cosmos DB account | ARM `Microsoft.DocumentDB/databaseAccounts`, Table API + serverless | **BLOCKED** |
| Cosmos Table | ARM `databaseAccounts/tables`, default `VisitorCounter` | **BLOCKED** |
| Function App | ARM Linux Function App, Python 3.12 | **BLOCKED** |
| Linux Consumption plan | ARM `Microsoft.Web/serverfarms`, SKU `Y1` / Dynamic | **BLOCKED** |
| Managed identity | ARM Function App `SystemAssigned` identity | **BLOCKED** |
| Cosmos RBAC | ARM table-scoped `tableRoleAssignments` using Function principal ID | **BLOCKED** |
| Application settings | ARM Function App `siteConfig.appSettings` | **BLOCKED** |
| CORS | ARM Function App CORS restricted to `corsAllowedOrigin` | **BLOCKED** |
| Application Insights/logging | No independently verified production telemetry resource/runtime evidence available | **BLOCKED** |

## Functional verification

| Check | Expected evidence | Result |
|---|---|---|
| Load deployed static website | Successful HTTPS response from approved public hostname | **BLOCKED** |
| Load frontend JavaScript | Deployed page loads `script.js` successfully | **BLOCKED** |
| Call visitor-counter API | `GET /api/visitors` returns approved success contract | **BLOCKED** |
| Verify API response contract | HTTP status, JSON schema, request ID, count semantics | **BLOCKED** |
| Verify Cosmos persistence | Counter entity changes in `VisitorCounter/Global` | **BLOCKED** |
| Call API again | Second approved synthetic call completes successfully | **BLOCKED** |
| Verify count change | Persisted count increments according to approved semantics | **BLOCKED** |
| Verify frontend display | Returned count is rendered in `#visitor-count` | **BLOCKED** |
| Verify expected error behavior | Invalid/rejected requests return canonical error contract without increment | **BLOCKED** |
| Verify logs | Function/runtime logs contain corresponding request evidence | **BLOCKED** |

## Production-data handling

No production Azure data was modified by this verification activity.

No visitor-counter synthetic state was created because the production API could not be reached.

## GitHub workflow evidence reviewed

### Backend

`.github/workflows/backend-ci.yml` contains the approved production sequence:

1. Authenticate to Azure with OIDC.
2. Validate the ARM template.
3. Deploy the ARM template.
4. Assert ARM provisioning state is `Succeeded`.
5. Package the Function application.
6. Deploy the Function application.
7. Upload `arm-deployment.json` and `deployment-evidence.txt`.

The workflow is implementation evidence, not proof that a production run succeeded.

### Frontend

`.github/workflows/deploy-frontend.yml` contains the approved production sequence:

1. Validate required static artifacts and fail-closed credential checks.
2. Build `dist/`.
3. Authenticate to Azure with OIDC.
4. Upload `dist/` to the Storage `$web` container using Microsoft Entra authorization.
5. Perform an HTTPS smoke check against `PUBLIC_HOSTNAME`.
6. Upload deployment evidence.

The workflow is implementation evidence, not proof that a production run succeeded.

The frontend PR CI workflow `.github/workflows/frontend-ci.yml` is also now present on `main`, with a PR job named `validate`.

## Required evidence to unblock

The following evidence must be obtained from an authenticated production execution before any live check can be marked PASS:

- Azure resource-group existence and deployment-state evidence.
- ARM deployment result with provisioning state `Succeeded`.
- Independent resource inventory for Storage, Cosmos Table, Function App, Consumption plan, managed identity and RBAC.
- Effective Function App application settings and CORS.
- Application Insights / Function runtime telemetry evidence.
- Public HTTPS hostname and successful static-site response.
- Successful `GET /api/visitors` response matching the frozen API contract.
- Before/after counter persistence evidence using only approved synthetic visitor state.
- Negative/error-path response evidence.
- Correlated Function logs for the verification requests.
- Retained GitHub Actions deployment artifacts.

## Current conclusion

**Phase 7 live Azure deployment verification: BLOCKED.**

No Azure resource, deployment, runtime, persistence, frontend, API, or logging result is represented as passed without direct production evidence.

No Phase 8 work is initiated by this evidence record.
