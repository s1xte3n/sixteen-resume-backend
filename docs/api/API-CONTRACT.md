# API Contract — Phase 4

## Contract identity

- Contract: Azure Cloud Resume Challenge visitor-counter API
- Version: 1.1.0
- Status: Frozen / implementation-ready
- Public operation: `GET /api/visitors`
- Authentication: None
- Authorization: Public counter invocation
- Persistence boundary: Azure Function -> visitor-counter adapter -> Azure Cosmos DB Table API
- Browser direct database access: Prohibited

## Request

### Method and path

`GET /api/visitors`

### Headers

| Header | Required | Rules |
|---|---|---|
| `X-Request-ID` | No | If supplied, must be UUID v4. If omitted, the API generates one. |
| `Accept` | Recommended | Client should permit `application/json`. |
| `Content-Type` | No | No request body is defined; clients do not need to send this header. |
| `Origin` | Browser-generated | Must satisfy the configured production CORS policy. |

No authentication, API key, idempotency key, Cosmos credential, or Azure credential is part of the public contract.

### Query

No application query parameters are supported. A request containing query parameters is rejected with HTTP 400 and must not increment the counter.

### Body

No request body is supported. A non-empty body is rejected with HTTP 400 and must not increment the counter.

The contract does not define or require a request JSON schema.

## Success response

### HTTP 200

```json
{"count":42}
```

Rules:

- `count` is a JSON integer.
- `count >= 0`.
- The returned value is the persisted count after the current operation has been successfully committed.
- Each successfully committed request increments the persistent counter exactly once.
- The response includes `X-Request-ID`.
- A valid client-supplied UUID v4 is preserved; otherwise the API returns a generated UUID v4.

### Success headers

- `Content-Type: application/json`
- `X-Request-ID: UUID v4`

## Error response

Canonical shape:

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Safe client-facing message.",
    "requestId": "uuid-v4"
  }
}
```

Required fields:

- `error.code`
- `error.message`
- `error.requestId`

Optional:

- `error.details.timestamp` as RFC 3339 UTC.

### Status contract

| HTTP | Code | Condition | Counter mutation |
|---:|---|---|---|
| 400 | BAD_REQUEST | Invalid request ID, unsupported query, or request body | No |
| 405 | METHOD_NOT_ALLOWED | Method other than GET | No |
| 429 | RATE_LIMITED | Platform/runtime throttling | No successful increment is claimed |
| 500 | INTERNAL_ERROR | Unexpected server/runtime/configuration failure | No unconfirmed increment |
| 503 | DEPENDENCY_UNAVAILABLE | Counter persistence dependency unavailable before commit | No successful increment |
| 504 | DEPENDENCY_TIMEOUT | Counter persistence dependency exceeded its configured boundary | Result is treated as unknown |

A 401/403 response is not part of normal public browser behavior because there is no end-user authentication. A Function-to-Cosmos authorization failure is an internal failure and maps safely to 500.

CORS rejection is a browser/platform boundary behavior and is not required to use the application JSON envelope.

## Concurrency and persistence

The persistence adapter uses one logical counter entity:

- PartitionKey: internal stable key
- RowKey: internal stable key
- Count: integer >= 0

The backend performs a concurrency-safe read/increment/conditional-write flow. Known optimistic-concurrency conflicts may be retried before a successful commit is confirmed. An ambiguous write outcome must not be blindly repeated.

Concurrent successful operations must not lose increments.

## Idempotency and retry

VC-001 is intentionally non-idempotent.

- One successful request is one counter operation.
- A refresh is another operation.
- No `Idempotency-Key` is supported.
- The frontend must not automatically retry a timeout or unknown network outcome.
- Server retries are limited to known safe concurrency conflicts before commit confirmation.

## CORS

Production CORS must:

- allow only the final approved resume origin;
- allow GET;
- allow the documented browser request headers when required;
- disallow credentials;
- prohibit wildcard production origin.

The exact production origin is deployment configuration and is not invented by this contract.

## Security boundary

The browser never receives:

- Cosmos credentials;
- Azure credentials;
- connection strings;
- database partition/row identifiers;
- internal provider exceptions.

The Function uses its approved managed identity for Cosmos data-plane access.

## Compatibility

The MVP route is fixed as `/api/visitors`.

Within this contract:

- `count` remains required and remains a non-negative JSON integer.
- Existing fields cannot be renamed, removed, or change type without an approved contract change.
- No new required request field may be introduced without an approved contract change.
- Breaking changes require synchronized contract, frontend, backend, and test updates.
