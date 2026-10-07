# API Variables

## VC-001 — GET /api/visitors

### Request

| Variable | Direction | Required | Type | Validation |
|---|---|---:|---|---|
| `Origin` | Request | Browser-generated | string | Must match production CORS allowlist |
| `Accept` | Request | Recommended | media type | Should permit `application/json` |
| `X-Request-ID` | Request | No | UUID string | UUID v4 when present |
| Query parameters | Request | No | — | None supported |
| Body | Request | No | — | Must be absent/empty |

### Response

| Variable | Direction | Required | Type | Validation |
|---|---|---:|---|---|
| `Content-Type` | Response | Yes | media type | `application/json` |
| `X-Request-ID` | Response | Yes | UUID string | UUID v4 |
| `count` | Body | Yes | integer | >= 0 |

### Error response

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `error.code` | string | Yes | Uppercase identifier |
| `error.message` | string | Yes | 1–256 characters |
| `error.requestId` | UUID string | Yes | UUID v4 |
| `error.details.timestamp` | date-time | No | RFC 3339 UTC |

## Internal DB-001 variables

| Variable | Type | Public | Rule |
|---|---|---:|---|
| `PartitionKey` | string | No | Stable internal logical partition |
| `RowKey` | string | No | Stable internal counter entity |
| `Count` | integer | No | >= 0 |
| Entity version/ETag | provider-specific | No | Used for concurrency control |

## Identifier rules

- `X-Request-ID`: UUID v4.
- No visitor/user identifier.
- No session identifier.
- No IP address field.
- No Cosmos `PartitionKey` or `RowKey` exposed publicly.
