# sixteen-resume-backend

Backend for the Azure Cloud Resume Challenge.

## Phase 7.2 — Persistence-backed visitor counter

The backend exposes the frozen visitor-counter contract:

`GET /api/visitors`

Local runtime target:

`http://localhost:7071/api/visitors`

### Persistence boundary

The application has a persistence adapter for Azure Cosmos DB Table API.

- Local Functions development uses Azurite Table Storage through `AZURE_TABLE_CONNECTION_STRING=UseDevelopmentStorage=true`.
- Azure runtime uses `DefaultAzureCredential` against the Cosmos DB Table endpoint.
- The browser never accesses the table service.
- The counter is one logical entity: `PartitionKey=VisitorCounter`, `RowKey=Global`.
- Updates use ETag-based conditional replacement with retry-on-conflict behavior so concurrent successful operations do not silently lose increments.

The local in-memory counter remains the default when `VISITOR_COUNTER_BACKEND` is not set, which keeps direct unit tests deterministic. The provided `local.settings.json.example` selects the Azurite-backed table implementation for `func start`.

### Executable contract files

The canonical Phase 7.1 contract is stored under `docs/api/`: `API-CONTRACT.md`, `API-ENDPOINTS.md`, `API-SCHEMAS.md`, `API-ERRORS.md`, `API-VARIABLES.md`, `API-EXAMPLES.md`, `API-CHANGELOG.md`, and `openapi.yaml`.

## Phase 7.3 — Azure IaC / Infrastructure Integration

The committed ARM template is:

`infra/azure/azuredeploy.json`

It provisions the resolved Azure core infrastructure:

- Azure Storage static website hosting for the frontend.
- Azure Functions Linux Consumption hosting.
- Function host storage.
- Azure Cosmos DB for Table API in serverless capacity.
- The single `VisitorCounter` table.
- Function system-assigned managed identity.
- Cosmos DB for Table native data-plane contributor access scoped to the counter table.
- Production CORS restricted to the approved frontend HTTPS origin.

The public HTTPS/CDN delivery resource is intentionally **not** included yet. ADR-006 leaves the exact edge service/SKU as an implementation-time selection that must first satisfy current availability/lifecycle, FreeDNS hostname compatibility, Storage origin compatibility, IaC support, and the R100/month recurring cost ceiling.

### ARM validation

Run from an authenticated Azure CLI context against the approved production resource group:

```bash
az deployment group validate \
  --resource-group "<RESOURCE_GROUP>" \
  --template-file infra/azure/azuredeploy.json \
  --parameters \
    frontendStorageAccountName="<FRONTEND_STORAGE_ACCOUNT>" \
    functionStorageAccountName="<FUNCTION_STORAGE_ACCOUNT>" \
    functionPlanName="sixteen-resume-functions" \
    functionAppName="<FUNCTION_APP_NAME>" \
    cosmosAccountName="<COSMOS_ACCOUNT_NAME>" \
    corsAllowedOrigin="https://<APPROVED_PUBLIC_HOSTNAME>"
```

A real Azure deployment validation cannot be claimed from source inspection alone. It requires an authenticated Azure context and an existing resource group.

### ARM deployment

Do not deploy the template to production until the Phase 7.3 implementation gates are satisfied:

```bash
az deployment group create \
  --resource-group "<RESOURCE_GROUP>" \
  --template-file infra/azure/azuredeploy.json \
  --parameters \
    frontendStorageAccountName="<FRONTEND_STORAGE_ACCOUNT>" \
    functionStorageAccountName="<FUNCTION_STORAGE_ACCOUNT>" \
    functionPlanName="sixteen-resume-functions" \
    functionAppName="<FUNCTION_APP_NAME>" \
    cosmosAccountName="<COSMOS_ACCOUNT_NAME>" \
    corsAllowedOrigin="https://<APPROVED_PUBLIC_HOSTNAME>" \
  --name "sixteen-resume-core"
```

### Infrastructure tests

`tests/test_arm_template.py` verifies the committed ARM artifact structurally, including:

- required core Azure resource types;
- Storage static website configuration;
- Cosmos Table + serverless configuration;
- disabled Cosmos key authentication;
- Python Function configuration;
- production CORS parameterization;
- table-scoped Cosmos data-plane RBAC;
- absence of long-lived CI/Cosmos credential markers.

The backend CI workflow runs this infrastructure test before the Azurite and HTTP integration tests.

### Environment progression

Phase 7.1 establishes the local executable API at `http://localhost:7071`. Phase 7.2 establishes the persistence adapter and deterministic local persistence tests. Phase 7.3 establishes source-controlled Azure core infrastructure. Production deployment evidence remains pending until Azure validation/deployment, runtime RBAC verification, HTTPS/CDN selection, DNS/HTTPS validation, and cost evidence are complete.

## Local setup

1. Install Python 3.11 or later.
2. Create and activate a virtual environment.
3. Install dependencies:

`python -m pip install -r requirements.txt`

4. Install Azure Functions Core Tools v4.
5. Install Azurite.
6. Copy `local.settings.json.example` to `local.settings.json`.
7. Start Azurite before the Functions host:

`azurite --silent`

8. In a second terminal start the Functions host:

`func start`

9. Call:

`curl -i http://localhost:7071/api/visitors`

The local table-backed counter persists in Azurite storage between Function restarts unless the Azurite data directory is removed.

## Tests

Run the complete local backend test suite:

`pytest -q`

Run the committed ARM structure tests:

`pytest -q tests/test_arm_template.py`

Run the Azurite persistence integration tests:

`RUN_AZURITE_TESTS=true pytest -q tests/test_table_counter.py`

With Azurite and the local Functions host running, execute the HTTP contract suite:

`RUN_FUNCTION_HOST_TESTS=true pytest -q tests/test_http_contract.py`

The HTTP contract suite validates the actual local Functions host route, including successful increments, request-ID handling, query/body validation, unsupported methods, content-type validation, canonical error shapes, and the no-increment behavior of rejected requests.

## CI

`.github/workflows/backend-ci.yml` is the backend validation gate. It runs:

1. deterministic Python tests;
2. committed ARM infrastructure tests;
3. Azurite-backed persistence tests;
4. Azure Functions Core Tools startup;
5. executable HTTP contract tests against `http://127.0.0.1:7071`.

The workflow does not yet perform a production Azure deployment. That belongs to the later CI/CD delivery gate after the required OIDC identity, RBAC scopes, Azure environment, HTTPS/CDN decision, and release conditions are verified.

## Azure authentication

Production application access does not use Cosmos connection strings or account keys. The Function uses its managed identity and Azure Cosmos DB for Table native data-plane RBAC. The Azure SDK's `DefaultAzureCredential` is used by the table adapter for the Azure runtime.

The classic Consumption hosting model requires Azure Functions host storage configuration. The ARM template derives the platform storage connection string at deployment time rather than committing a credential to source; it is not emitted as an ARM output.

GitHub-to-Azure OIDC for backend deployment is a separate delivery/identity configuration and is not hardcoded in this repository.

No Azure credentials, Cosmos credentials, or CI secrets belong in source control.
