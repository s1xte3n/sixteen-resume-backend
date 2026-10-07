# Phase 3 Gate Remediation

## Confirmed blockers

1. Frontend CI authenticates successfully but `az storage blob upload-batch --auth-mode login` fails because the deployment service principal lacks **Storage Blob Data Contributor** on `st16resumeweb`.
2. Backend ARM validation fails because the deployment service principal lacks **Microsoft.Authorization/roleAssignments/write** on the production resource group. The deployment identity therefore requires **User Access Administrator** at the resource-group scope in addition to its approved deployment permissions.

## Required remediation

- Grant the frontend GitHub Actions service principal Storage Blob Data Contributor on the frontend storage-account scope.
- Grant the backend GitHub Actions service principal User Access Administrator on `rg-sixteen-resume-prod`.
- Do not use Owner, client secrets, publish profiles, or storage account keys as workarounds.
- Verify the assignments by principal object ID before rerunning CI.
- Rerun backend and frontend production workflows and retain fresh successful OIDC, ARM, deployment, storage-upload, and API verification evidence.

## Gate status

**BLOCKED** until fresh production workflow evidence demonstrates successful authentication and all required deployment/data-plane operations.
