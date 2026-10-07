# Phase 3 Gate Remediation

## Current Phase 3 blocker

The Azure infrastructure and GitHub OIDC authorization blockers have been remediated. The remaining backend blocker is **Flex Consumption runtime readiness**: infrastructure validation/deployment succeeds and the Function App reports the expected Flex configuration, but the production `GET /api/visitors` probe returns HTTP 503 during post-package verification.

The application already maps dependency failures to HTTP 503, so the verification must distinguish a normal platform cold start from an application dependency/RBAC failure.

## Remediation applied

1. **Use the Flex-supported Python deployment path.** The workflow now creates `released-package.zip` from the Python project source and deploys it with Azure CLI `az functionapp deployment source config-zip --build-remote true`. This avoids locally vendoring Python dependencies and lets Azure perform the Linux-compatible remote build required for Python Flex deployments.

2. **Allow infrastructure/RBAC propagation before code deployment.** The workflow now waits after ARM deployment, verifies the Function App managed identity can see its Cosmos Table data-plane assignment, and verifies the required Function host-storage roles before package deployment.

3. **Make readiness diagnostics actionable.** The production HTTP probe now records the actual HTTP status and response body instead of treating every `curl` failure as an indistinguishable startup timeout. The verification window was extended to 18 attempts.

4. **Preserve least privilege.** No storage keys, client secrets, direct Cosmos access from the frontend, or subscription-wide deployment permissions are introduced. The existing managed-identity assignments remain the approved model.

## Verification required

The Phase 3 backend gate is cleared only when a fresh production workflow demonstrates:

- OIDC authentication succeeds with the recreated backend application registration.
- ARM validation and deployment succeed.
- Flex runtime configuration is correct.
- Function host-storage and Cosmos Table RBAC assignments are visible to the Function App identity.
- Python package deployment completes through the Flex package deployment path.
- `GET /api/visitors` returns a successful response from the deployed Function App.

If the HTTP probe still returns 503 after these changes, use the captured response body and Azure Function/Application Insights runtime logs to identify the remaining application dependency failure rather than extending the timeout again.

## Gate status

**BLOCKED — one backend Phase 3 runtime-readiness blocker remains: production `GET /api/visitors` must pass after the corrected Flex Python deployment and RBAC propagation handling.**
