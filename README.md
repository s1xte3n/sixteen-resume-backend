# sixteen-resume-backend

Backend for the Azure Cloud Resume Challenge.

## Phase 7.1 — Backend foundation

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

### Local setup

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

### Tests

Run deterministic unit and component tests:

`pytest -q`

Run the Azurite persistence integration tests:

`RUN_AZURITE_TESTS=true pytest -q tests/test_table_counter.py`

With Azurite and the local Functions host running, execute the HTTP contract suite:

`RUN_FUNCTION_HOST_TESTS=true pytest -q tests/test_http_contract.py`

The HTTP contract suite validates the actual local Functions host route, including successful increments, request-ID handling, query/body validation, unsupported methods, content-type validation, canonical error shapes, and the no-increment behavior of rejected requests.

### CI

`.github/workflows/backend-ci.yml` is the backend validation gate. It runs:

1. deterministic Python tests;
2. Azurite-backed persistence tests;
3. Azure Functions Core Tools startup;
4. executable HTTP contract tests against `http://127.0.0.1:7071`.

The workflow does not deploy Azure resources. Deployment and infrastructure remain later Phase 7 work.

### Azure authentication

Production does not use Cosmos connection strings or account keys. The Function uses its managed identity and Azure Cosmos DB for Table native data-plane RBAC. The Azure SDK's `DefaultAzureCredential` is used by the table adapter for the Azure runtime.

No Azure credentials, connection strings, or production secrets belong in source control.
