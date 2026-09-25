# API Errors

Canonical envelope:

```json
{"error":{"code":"ERROR_CODE","message":"Human-readable message.","requestId":"uuid-v4"}}
```

| Code | HTTP | Meaning |
|---|---:|---|
| BAD_REQUEST | 400 | Invalid request input or unsupported query/body. |
| UNSUPPORTED_MEDIA_TYPE | 415 | Supplied Content-Type is not application/json. |
| METHOD_NOT_ALLOWED | 405 | Request method is not GET. |
| DEPENDENCY_UNAVAILABLE | 503 | Counter persistence dependency is unavailable. |
| DEPENDENCY_TIMEOUT | 504 | Counter persistence dependency timed out. |
| INTERNAL_ERROR | 500 | Unexpected server failure. |

Rejected requests must not increment the counter.
