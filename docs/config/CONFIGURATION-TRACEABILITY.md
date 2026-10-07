# Phase 5 — Configuration Traceability

| Config area | Requirement IDs | Contract/Deployment IDs | ADRs | Verification/Test IDs |
|---|---|---|---|---|
| Azure region/resource deployment | REQ-AZ-012, REQ-AZ-REG-001, REQ-AZ-DEV-001 | DEP-002 | ADR-005 | VT-012, VT-REG-001, VT-IAC-001, T-012-P, T-IAC-001 |
| Visitor API path/origin boundary | REQ-AZ-007, REQ-AZ-009, REQ-AZ-015 | VC-001 | ADR-002/visitor API decision | VT-007, VT-009, VT-015, T-009-P, T-009-N |
| Cosmos persistence/table | REQ-AZ-008, REQ-AZ-010 | DB-001, VC-001 | ADR-003, runtime identity ADRs | VT-008, VT-010, T-DATA-001, T-DATA-002 |
| Function runtime | REQ-AZ-010, REQ-AZ-FLEX-001..013 | DEP-002 | current Flex ADR/architecture baseline | VT-010, VT-FLEX-001..013, T-FLEX-001..013 |
| Backend CI/CD | REQ-AZ-011, REQ-AZ-013, REQ-AZ-SEC-001, REQ-AZ-SEC-003 | DEP-002 | ADR-005 | VT-011, VT-013, VT-SEC-001, VT-SEC-003, T-013-P, T-013-SEC |
| Frontend CI/CD | REQ-AZ-014, REQ-AZ-SEC-001, REQ-AZ-SEC-003 | DEP-001 | ADR-004/005 | VT-014, VT-SEC-001, VT-SEC-003, T-014-P, T-014-SEC |
| Storage static website | REQ-AZ-004 | DEP-001 | frontend infrastructure ADRs | VT-004, T-004-P |
| HTTPS/hostname/CORS | REQ-AZ-005, REQ-AZ-006, REQ-AZ-SEC-004, REQ-AZ-COST-001 | DNS-001, DEP-001 | ADR-006 | VT-005, VT-006, VT-SEC-004, VT-COST-001, T-005-P, T-006-P |
| Browser/Cosmos isolation | REQ-AZ-SEC-002 | VC-001, DB-001 | security architecture | VT-SEC-002, T-009-SEC |
| OIDC/RBAC | REQ-AZ-SEC-001, REQ-AZ-SEC-003, REQ-AZ-013, REQ-AZ-014 | DEP-001, DEP-002 | ADR-005 | VT-SEC-001, VT-SEC-003, T-013-SEC, T-014-SEC |
| Test state/data | REQ-AZ-011, REQ-AZ-015 | DEP-001/002 test interfaces | test strategy | T-011-P, T-DATA-001, T-DATA-002, T-015-E2E |

## Traceability gaps

No approved requirement requires a secret value. The remaining configuration gaps are external provisioning/acceptance gates: final edge service, public hostname, final CORS origin, live OIDC/RBAC evidence, live endpoints, and cost evidence.

No API contract field is being converted into environment configuration.
