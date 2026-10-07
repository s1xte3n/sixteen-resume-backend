# API Endpoints

| Contract ID | Method | Path | Auth | Priority | Status | Requirement |
|---|---|---|---|---|---|---|
| API-001 | GET | /api/visitors | Anonymous | P0 | Executable | Visitor counter / API requirement |

The route intentionally accepts other HTTP methods at the Azure Functions trigger so the application can return the canonical 405 contract instead of relying on platform-generated errors.
