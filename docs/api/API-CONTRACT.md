# API Contract — Phase 7.1

## Contract identity

- Contract: API-001
- Version: 1.0.0
- Status: Executable
- Base URL (local): http://localhost:7071
- Resource: /api/visitors
- Operation: GET /api/visitors
- Authentication: Anonymous
- Authorization: Public read/increment operation
- Persistence boundary: Azure Function -> visitor-counter adapter -> Azure Cosmos DB Table API
- Browser direct database access: Prohibited

## Request

### Method and path

`GET /api/visitors`

### Headers

| Header | Required | Rules |
|---|---|---|
| X-Request-ID | No | If supplied, must be a UUID v4. If omitted, the API generates one. |
| Content-Type | No | If supplied, media type must be `application/json`. |
| Other headers | No | Ignored unless enforced by the platform. |

### Query

No query parameters are supported. Any query parameter causes HTTP 400 and must not increment the counter.

### Body

No request body is supported. A non-empty body causes HTTP 400 and must not increment the counter.

## Success response

### HTTP 200

```json
{"count": 42}
```

Rules:

- `count` is an integer.
- Each accepted GET increments the persistent counter exactly once.
- The response includes `X-Request-ID`.
- A client-supplied valid UUID v4 is preserved.
- A generated request ID is UUID v4.

## Error response

Canonical shape:

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Human-readable message.",
    "requestId": "uuid-v4"
  }
}
```

### Status contract

| HTTP | Code | Condition | Counter mutation |
|---:|---|---|---|
| 400 | BAD_REQUEST | Invalid X-Request-ID, unsupported query, or request body | No |
| 405 | METHOD_NOT_ALLOWED | Method other than GET | No |
| 415 | UNSUPPORTED_MEDIA_TYPE | Unsupported Content-Type | No |
| 503 | DEPENDENCY_UNAVAILABLE | Counter persistence dependency unavailable | No successful increment |
| 504 | DEPENDENCY_TIMEOUT | Counter persistence dependency timed out | No successful increment |
| 500 | INTERNAL_ERROR | Unexpected server failure | No successful increment |

All error responses include `X-Request-ID` and the same ID inside `error.requestId`.

## Concurrency and persistence

The persistence adapter uses the single logical entity:

- PartitionKey: `VisitorCounter`
- RowKey: `Global`
- Property: `Count`

Updates use ETag/If-Not-Modified conditional replacement and retry on concurrent modification. A successful concurrent request must not silently lose an increment.

## Versioning

The initial MVP contract is unversioned at the path level. Breaking changes require a contract change record and synchronized frontend/test updates. Non-breaking response/header additions must still be reviewed against the acceptance criteria before adoption.
