# API Errors

## Canonical envelope

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Safe client-facing message.",
    "requestId": "uuid-v4"
  }
}
```

Optional `error.details.timestamp` may be included as RFC 3339 UTC.

| Code | HTTP | Meaning |
|---|---:|---|
| BAD_REQUEST | 400 | Request violates the VC-001 interface; no counter mutation. |
| METHOD_NOT_ALLOWED | 405 | Request method is not GET; no counter mutation. |
| RATE_LIMITED | 429 | Platform/runtime throttling; no successful increment is claimed. |
| INTERNAL_ERROR | 500 | Unexpected server/runtime/configuration failure. |
| DEPENDENCY_UNAVAILABLE | 503 | Counter persistence dependency unavailable before commit. |
| DEPENDENCY_TIMEOUT | 504 | Counter dependency exceeded its configured time boundary; result is unknown to the caller. |

There is no public 401/403 contract because VC-001 has no end-user authentication. Backend identity/RBAC failure against Cosmos is mapped to `500 INTERNAL_ERROR`.

There is no public 415 contract. Content-Type is not an application validation dimension because VC-001 defines no request body. A non-empty body is rejected as `400 BAD_REQUEST`.

CORS failures are browser/platform boundary behavior and are not guaranteed to use this JSON envelope.

## Safe exposure

Never return stack traces, secrets, tokens, connection strings, Cosmos credentials, raw provider exceptions, or unnecessary internal resource identifiers.

## Retry semantics

The operation is non-idempotent. Clients must not automatically retry timeout or unknown-outcome requests. The backend may retry only known optimistic-concurrency conflicts before commit confirmation.
