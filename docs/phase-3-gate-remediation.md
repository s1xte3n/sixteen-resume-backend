# Phase 3 Gate Remediation

## Current Phase 3 blocker

The backend has two current findings. First, the failed production deployment used stale Cosmos DB API version `2024-08-15-preview`, which is not registered for the approved East US deployment; the authoritative `main` template now uses `2023-04-15` for the Cosmos account and `2026-03-15` for Table role assignments. Second, the Function App can start with the expected Flex configuration but `GET /api/visitors` returns `503 DEPENDENCY_UNAVAILABLE` when Cosmos Table access is unavailable.

The application already maps dependency failures to HTTP 503, so the verification must distinguish a normal platform cold start from an application dependency/RBAC failure.

## Remediation applied

1. **Pin the supported Cosmos management API contract.** The authoritative ARM template uses `Microsoft.DocumentDB/databaseAccounts@2023-04-15`; the Table role-assignment resource uses `2026-03-15`.

2. **Use the Flex-supported Python deployment path.** The workflow now creates `released-package.zip` from the Python project source and deploys it with Azure CLI `az functionapp deployment source config-zip --build-remote true`. This avoids locally vendoring Python dependencies and lets Azure perform the Linux-compatible remote build required for Python Flex deployments.

3. **Allow infrastructure/RBAC propagation before code deployment.** The workflow now waits after ARM deployment, verifies the Function App managed identity can see its Cosmos Table data-plane assignment, and verifies the required Function host-storage roles before package deployment.

4. **Make readiness diagnostics actionable.** The production HTTP probe now records the actual HTTP status and response body instead of treating every `curl` failure as an indistinguishable startup timeout. The verification window was extended to 18 attempts.

5. **Preserve least privilege.** No storage keys, client secrets, direct Cosmos access from the frontend, or subscription-wide deployment permissions are introduced. The existing managed-identity assignments remain the approved model.

## Verification required

The Phase 3 backend gate is cleared only when a fresh production workflow demonstrates:

- OIDC authentication succeeds with the recreated backend application registration.
- ARM validation and deployment succeed without an unregistered Cosmos API version.
- Flex runtime configuration is correct.
- Function host-storage and Cosmos Table RBAC assignments are visible to the Function App identity.
- Python package deployment completes through the Flex package deployment path.
- `GET /api/visitors` returns a successful response from the deployed Function App.

If the HTTP probe still returns `503 DEPENDENCY_UNAVAILABLE` after successful ARM deployment and RBAC checks, diagnose Cosmos Table runtime access from Function/Application Insights logs rather than extending the timeout.

## Gate status

**BLOCKED — the next production run must prove successful ARM deployment with the pinned Cosmos API and successful Cosmos-backed `GET /api/visitors`.**
