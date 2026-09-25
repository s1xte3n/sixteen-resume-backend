# sixteen-resume-backend

Backend for the Azure Cloud Resume Challenge.

## Phase 7.1 — Local backend foundation

The current foundation implements the frozen MVP HTTP contract for:

`GET /api/visitors`

Local runtime target:

`http://localhost:7071/api/visitors`

### Current persistence boundary

Phase 7.1 uses a thread-safe in-memory repository so the HTTP contract and application behavior can be executed locally without provisioning Azure resources.

This is intentionally not production persistence. The Cosmos DB Table API repository and managed-identity integration are later implementation work.

### Local setup

1. Install Python 3.11 or later.
2. Create and activate a virtual environment.
3. Install dependencies:

`pip install -r requirements.txt`

4. Install Azure Functions Core Tools v4.
5. Copy `local.settings.json.example` to `local.settings.json`.
6. Start the function host:

`func start`

7. Call:

`curl -i http://localhost:7071/api/visitors`

### Tests

Run:

`pytest`

The test suite validates the local executable contract, including success, request IDs, method/content/query/body validation, canonical errors, and concurrent increments.

No Azure credentials or production secrets belong in `local.settings.json.example` or source control.
