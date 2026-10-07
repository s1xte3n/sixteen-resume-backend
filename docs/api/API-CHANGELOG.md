# API Contract Changelog

## 1.1.1 — Phase 4 executable contract-test alignment

- Corrected the HTTP contract test to accept a bodyless request with an arbitrary Content-Type, matching the frozen VC-001 contract.
- Kept non-empty request bodies mapped to 400 BAD_REQUEST.
- Removed the stale executable expectation for 415 UNSUPPORTED_MEDIA_TYPE.
- No API route, payload, persistence, authentication, authorization, or architecture behavior changed.

# API Contract Changelog

## 1.1.0 — Phase 4 contract alignment

- Aligned backend documentation with the frozen `GET /api/visitors` contract.
- Removed the backend-only `415 UNSUPPORTED_MEDIA_TYPE` status from the public contract.
- Standardized unsupported query/body input on `400 BAD_REQUEST`.
- Standardized `count` as an integer >= 0.
- Standardized canonical error taxonomy to 400/405/429/500/503/504.
- Documented `X-Request-ID` as a response correlation header.
- Preserved anonymous public access, non-idempotent counter semantics, managed-identity Cosmos access, and concurrency-safe persistence.
- Kept browser-to-Cosmos access prohibited.

## 1.0.0 — Phase 7.1

Initial executable visitor-counter contract. Superseded where it differed from the approved Phase 4 contract.
