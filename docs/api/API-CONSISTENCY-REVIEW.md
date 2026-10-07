# Phase 4 API Contract Consistency Review

## Gate

**CONTRACT READY — PASS at contract-definition level**

A frontend client can implement VC-001 from the frozen contract without reading backend source.

## Corrected mismatches

| Finding | Previous backend definition | Frozen Phase 4 definition | Resolution |
|---|---|---|---|
| Unsupported media type | 415 UNSUPPORTED_MEDIA_TYPE | No 415 public contract | Removed |
| Unsupported body/query | 400 plus 415 content-type path | 400 BAD_REQUEST | Standardized |
| Success count lower bound | count >= 1 | count >= 0 | Corrected |
| Error taxonomy | Included 415 | 400/405/429/500/503/504 | Standardized |
| Correlation header | Returned by backend but not fully documented cross-repo | X-Request-ID documented request/response header | Documented in both repos |
| OpenAPI | Backend omitted several canonical statuses | Contract-aligned statuses and schemas | Corrected |

## Frozen cross-repository contract

- Public operation: `GET /api/visitors`
- No authentication.
- No query parameters.
- No request body.
- Invalid request data: `400 BAD_REQUEST`.
- Unsupported methods: `405 METHOD_NOT_ALLOWED`.
- Platform throttling: `429 RATE_LIMITED`.
- Unexpected failure: `500 INTERNAL_ERROR`.
- Dependency unavailable: `503 DEPENDENCY_UNAVAILABLE`.
- Dependency timeout: `504 DEPENDENCY_TIMEOUT`.
- Success body: `{ "count": <integer >= 0> }`.
- `X-Request-ID` is optional on request and required as a UUID v4 response correlation header.
- Counter operation is non-idempotent.
- Frontend must not automatically retry an ambiguous timeout/network outcome.
- Browser never communicates directly with Cosmos DB.

## Scope control

No new endpoint, feature, authentication model, persistence model, or architecture change was introduced.

The backend request-validation implementation was corrected only to remove behavior that contradicted the frozen contract: content-type-specific `415` handling. Non-empty bodies remain rejected with `400 BAD_REQUEST`.

## Remaining evidence

This gate establishes interface-definition readiness. Runtime, Azure, CORS, concurrency, deployment, and end-to-end test evidence remain later implementation/verification activities.