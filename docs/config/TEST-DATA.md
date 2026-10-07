# Phase 5 — Generated Test State & Synthetic Data

## Principles

Test state is not production configuration and is not a secret. All test data is synthetic.

## Generated test state

| ID | State | Context | Source | Reset/cleanup | Production allowed |
|---|---|---|---|---|---|
| TEST-001 | Azurite Table service | local/test/CI | Azurite | Delete test table after test | No |
| TEST-002 | Unique test table name `VisitorCounter<uuid>` | persistence tests | generated per test | Delete table in finally/cleanup | No |
| TEST-003 | Synthetic counter entity | local/test/CI | test fixture | Recreate or delete per test | No |
| TEST-004 | X-Request-ID UUID v4 | API tests | generated/test fixture | Request-scoped | No |
| TEST-005 | FUNCTION_BASE_URL=http://127.0.0.1:7071 | CI HTTP contract tests | local Functions host | Process-scoped | No |
| TEST-006 | RUN_AZURITE_TESTS=true | CI | workflow | Job-scoped | No |
| TEST-007 | Local Functions settings from local.settings.json.example | CI/local | repository example | Delete generated local.settings.json after run where practical | No |
| TEST-008 | Postman apiBaseUrl/publicOrigin/requestId | API client | generated local environment | Untracked environment; replace per deployment | No production credentials |

## Synthetic API data

Valid:
- Empty GET request to /api/visitors.
- Optional UUID v4 `X-Request-ID`.

Invalid:
- Query parameter, e.g. `?unexpected=value`.
- Non-empty request body.
- Invalid UUID in `X-Request-ID`.
- Unsupported method.
- Dependency unavailable/timeout via test seam or controlled integration failure.

Expected persistence:
- Counter is an integer >= 0.
- Concurrent successful increments must not lose updates.
- Test state is isolated from production.

## Failure injection

Approved failure cases are test seams already represented by the backend domain/adapter tests:
- dependency timeout → 504.
- dependency unavailable → 503.
- invalid persisted count → dependency failure.
- concurrent conditional-write conflict → bounded retry before commit confirmation.

Do not add production-only switches solely to make failure injection easier.

## Security test data

Use only synthetic UUIDs, table names, counters, and malformed request data. No real names, email addresses, credentials, Azure IDs requiring confidentiality, or production visitor data are needed.

## Cleanup

Automated tests must remove temporary tables and stop local emulators/Function hosts. A failed test must not silently leave state that can affect another test.
