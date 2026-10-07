# API Endpoints

## Public application endpoints

| Contract ID | Method | Path | Auth | Authorization | Priority | Status | Requirements |
|---|---|---|---|---|---|---|---|
| VC-001 | GET | /api/visitors | None | Public counter invocation | P1 | Frozen / implementation-ready | REQ-AZ-007..010 |

## Public method behavior

`GET /api/visitors` is the only supported application operation.

Unsupported HTTP methods must return the canonical `405 METHOD_NOT_ALLOWED` error envelope and must not mutate counter state.

## Public non-endpoints

The v1 public API intentionally exposes no authentication, admin/reset, analytics, user/profile, health, pagination/filtering, or Cosmos DB endpoint.

## Architecturally significant internal interfaces

| Contract ID | Interface | Direction | Requirements |
|---|---|---|---|
| DB-001 | VisitorCounter persistence | Azure Function -> Cosmos DB Table API | REQ-AZ-008, REQ-AZ-010, REQ-AZ-SEC-003 |
| DEP-001 | Frontend production publication | GitHub Actions -> Azure Storage/edge delivery | REQ-AZ-004, REQ-AZ-005, REQ-AZ-014 |
| DEP-002 | Backend production deployment | GitHub Actions -> ARM/Function/Cosmos | REQ-AZ-010..013, REQ-AZ-DEV-001, REQ-AZ-FLEX-001..013 |
| DNS-001 | Public hostname resolution | FreeDNS -> approved edge endpoint | REQ-AZ-006, REQ-AZ-015 |

## Governance

- VC-001 is the sole public application operation.
- Cosmos DB is never a public browser interface.
- No implementation may invent a second contract for the same operation.
- Any new public endpoint requires an approved requirements and contract change.
