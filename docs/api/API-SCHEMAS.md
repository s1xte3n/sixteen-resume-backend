# API Schemas

## 1. Schema conventions

- JSON property names use lower camel case.
- No request JSON schema is defined for VC-001.
- No success property is nullable.
- `count` is a JSON integer >= 0.
- Error timestamps, when present, are RFC 3339 UTC.
- Internal Cosmos fields are never public API fields.

## 2. VC-001 request

VC-001 is bodyless.

```http
GET /api/visitors HTTP/1.1
Accept: application/json
```

A non-empty request body is outside the contract and results in `400 BAD_REQUEST`. Query parameters are likewise outside the contract and result in `400 BAD_REQUEST`.

## 3. VC-001 success — VisitorCountResponse

```yaml
type: object
additionalProperties: false
required:
  - count
properties:
  count:
    type: integer
    minimum: 0
```

## 4. ErrorResponse

```yaml
type: object
additionalProperties: false
required:
  - error
properties:
  error:
    type: object
    additionalProperties: false
    required:
      - code
      - message
      - requestId
    properties:
      code:
        type: string
        pattern: '^[A-Z][A-Z0-9_]{2,63}$'
      message:
        type: string
        minLength: 1
        maxLength: 256
      requestId:
        type: string
        format: uuid
      details:
        type: object
        additionalProperties: false
        properties:
          timestamp:
            type: string
            format: date-time
```

## 5. Error code enum

- `BAD_REQUEST`
- `METHOD_NOT_ALLOWED`
- `RATE_LIMITED`
- `INTERNAL_ERROR`
- `DEPENDENCY_UNAVAILABLE`
- `DEPENDENCY_TIMEOUT`

## 6. Internal persistence schema

| Field | Type | Constraint |
|---|---|---|
| `PartitionKey` | string | Stable internal key |
| `RowKey` | string | Stable internal key |
| `Count` | integer | >= 0 |
| Entity version/ETag | provider-specific | Internal concurrency control |

The actual key values are not public API fields.
