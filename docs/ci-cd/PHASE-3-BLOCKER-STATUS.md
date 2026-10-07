# Phase 3 Blocker Status

## Scope

This document records the currently observed Phase 3 production deployment blockers. No API, hosting, storage, OIDC, or runtime architecture change is introduced.

## Backend — deployment identity lacks RBAC management permission

Fresh production ARM validation reached the approved template but failed because the GitHub OIDC deployment identity could not create the template's required `Microsoft.Authorization/roleAssignments` resources.

Observed permission failure: `Microsoft.Authorization/roleAssignments/write`.

### Required correction

The backend GitHub OIDC service principal must retain its existing deployment permissions and additionally have:

- **User Access Administrator**
- Scope: `/subscriptions/<subscription-id>/resourceGroups/rg-sixteen-resume-prod`

This is the minimum built-in role needed for the deployment identity to create the ARM role assignments already defined in the approved template. Do **not** grant Owner or subscription-wide Contributor as a workaround.

The ARM template remains responsible for assigning the Function App managed identity its existing narrow data-plane roles. The template is not redesigned to bypass RBAC.

### Command-line correction

Run as an administrator already authorized to assign RBAC at the resource-group scope:

```bash
SUBSCRIPTION_ID="aab5b649-b686-4f86-95cc-aa72ae71f03b"
RESOURCE_GROUP="rg-sixteen-resume-prod"
BACKEND_DEPLOYMENT_SP_OBJECT_ID="<backend-github-service-principal-object-id>"
UAA_ROLE_ID="f1a07417-d97a-45cb-824c-7a7467783830"

az account set --subscription "$SUBSCRIPTION_ID"

az role assignment create \
  --assignee-object-id "$BACKEND_DEPLOYMENT_SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "$UAA_ROLE_ID" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"
```

Verify the assignment before rerunning production.

## Frontend — storage data-plane permission missing

The frontend production workflow successfully reached the Azure storage deployment step but failed because its OIDC identity was not authorized for Microsoft Entra blob data access.

Required permission:

- **Storage Blob Data Contributor**
- Scope: production frontend storage account only: `st16resumeweb`

The existing workflow already uses `--auth-mode login`; no switch to storage keys, SAS, connection strings, or shared-key authentication is permitted.

### Command-line correction

Run as an administrator authorized to assign the storage data-plane role:

```bash
SUBSCRIPTION_ID="aab5b649-b686-4f86-95cc-aa72ae71f03b"
RESOURCE_GROUP="rg-sixteen-resume-prod"
FRONTEND_STORAGE_ACCOUNT="st16resumeweb"
FRONTEND_DEPLOYMENT_PRINCIPAL_OBJECT_ID="<frontend-oidc-principal-object-id>"

az account set --subscription "$SUBSCRIPTION_ID"

STORAGE_SCOPE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$FRONTEND_STORAGE_ACCOUNT"

az role assignment create \
  --assignee-object-id "$FRONTEND_DEPLOYMENT_PRINCIPAL_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_SCOPE"
```

Verify the assignment before rerunning production.

## Verification gate

Phase 3 remains **BLOCKED** until fresh production evidence proves:

1. Backend OIDC authentication succeeds.
2. Backend ARM validation/deployment can create its required role assignments.
3. Backend Function deployment reaches the existing HTTPS `GET /api/visitors` readiness check.
4. Frontend OIDC authentication succeeds.
5. Frontend storage upload succeeds using Microsoft Entra authorization.
6. No storage keys, SAS tokens, client secrets, or publish profiles are introduced.

These are RBAC corrections only; no product or architecture scope is changed.
