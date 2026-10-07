# Phase 5 — Configuration Validation Rules

## Global rules

| ID | Rule | Failure class |
|---|---|---|
| VAL-001 | Required configuration must exist before its consuming stage executes. | BLOCKER |
| VAL-002 | Unknown production values must be marked TBD/PENDING PROVISIONING, never guessed. | BLOCKER |
| VAL-003 | Production URLs must use HTTPS where a public HTTPS endpoint is required. | BLOCKER |
| VAL-004 | Production CORS must be one exact approved frontend origin; wildcard is prohibited. | BLOCKER |
| VAL-005 | Browser artifacts must contain no Azure/Cosmos credentials or connection strings. | BLOCKER |
| VAL-006 | Production must not use local/test connection strings, Azurite endpoints, or synthetic state. | BLOCKER |
| VAL-007 | API path remains exactly /api/visitors and is not configurable independently. | BLOCKER |
| VAL-008 | Cosmos endpoint must be generated from the deployed Cosmos account; it is not a credential. | WARNING if absent before deployment; BLOCKER at runtime |
| VAL-009 | Production Function Cosmos access must use the system-assigned managed identity and native Table RBAC. | BLOCKER |
| VAL-010 | CI/CD Azure authentication must use OIDC; long-lived Azure client secrets are prohibited. | BLOCKER |
| VAL-011 | Storage deployment must use Entra authorization, not Storage keys/SAS/connection strings. | BLOCKER |
| VAL-012 | Azure location must equal East US unless an approved architecture change exists. | BLOCKER |
| VAL-013 | Resource names must satisfy the constraints enforced by ARM parameters. | BLOCKER |
| VAL-014 | Flex runtime must be Linux FC1, Python 3.12, Functions v4, zero always-ready, 512 MB memory, maximum one instance. | BLOCKER |
| VAL-015 | `FUNCTIONS_WORKER_RUNTIME` must not be supplied as a production Flex app setting. | BLOCKER |
| VAL-016 | `FUNCTIONS_EXTENSION_VERSION` must not be treated as a production Flex requirement. | WARNING/BLOCKER if deployment depends on it |
| VAL-017 | Test identifiers/table names must not overlap production persistent state. | BLOCKER |
| VAL-018 | Secrets/credential-like values must not be written to logs, errors, responses, or evidence artifacts. | BLOCKER |
| VAL-019 | GitHub production variables must not be silently copied into repository source. | WARNING |
| VAL-020 | Public endpoint verification may be enabled only after the approved edge/DNS path exists. | BLOCKER if enabled prematurely |

## Validation ownership

- Application/runtime validation: backend/frontend owners.
- ARM validation: infrastructure owner.
- OIDC/RBAC validation: security + DevOps owner.
- Public hostname/CORS/edge values: release/infrastructure owner.
- Synthetic test state: QA owner.

## Configuration gates

1. **GATE-CFG-001:** final public hostname.
2. **GATE-CFG-002:** final HTTPS/edge service and endpoint.
3. **GATE-CFG-003:** exact production CORS origin derived from the final public frontend origin.
4. **GATE-CFG-004:** live GitHub production environment OIDC values and federated credentials.
5. **GATE-CFG-005:** live Azure RBAC evidence for backend deployment identity, frontend deployment identity, and Function managed identity.
6. **GATE-CFG-006:** live deployed API/Storage endpoints.
7. **GATE-CFG-007:** production cost evidence <= R100/month.
