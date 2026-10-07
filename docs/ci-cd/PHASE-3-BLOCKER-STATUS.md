# Phase 3 Blocker Status

## Scope

This document records the current Phase 3 production blockers. The remediation is limited to Azure RBAC; no API, hosting, storage, OIDC, or runtime architecture change is introduced.

## Backend — deployment identity lacks RBAC management permission

Fresh production ARM validation reached the approved template and failed because the GitHub OIDC deployment identity could not create the template's required `Microsoft.Authorization/roleAssignments` resources.

Observed action:
`Microsoft.Authorization/roleAssignments/write`

The failing deployment principal is the backend GitHub Actions OIDC service principal.

### Required correction

Assign **User Access Administrator** to the backend GitHub Actions service principal at:

`/subscriptions/<subscription-id>/resourceGroups/rg-sixteen-resume-prod`

This is the narrow built-in role required for the deployment identity to create the role assignments already declared by the approved ARM template. Do not grant Owner or subscription-wide Contributor as a workaround.

The ARM template remains responsible for assigning the Function App managed identity its existing narrow storage, queue, and Cosmos Table permissions.

### Command-line correction

Run these commands as an administrator whose identity already has `Microsoft.Authorization/roleAssignments/write` at the resource-group scope:

```bash
SUBSCRIPTION_ID="aab5f649-b686-4f86-95cc-aa72ae71f03b"
RESOURCE_GROUP="rg-sixteen-resume-prod"
UAA_ROLE_ID="f1a07417-d97a-45cb-824c-7a7467783830"

az account set --subscription "$SUBSCRIPTION_ID"

BACKEND_SP_OBJECT_ID="$(
  az ad sp list     --display-name "sixteen-resume-backend-github-actions"     --query "[0].id"     --output tsv
)"

test -n "$BACKEND_SP_OBJECT_ID"

az role assignment create   --assignee-object-id "$BACKEND_SP_OBJECT_ID"   --assignee-principal-type ServicePrincipal   --role "$UAA_ROLE_ID"   --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"
```

If `az role assignment create` reports the previously observed CLI subscription error, use the ARM REST API instead; this still requires the caller to possess `Microsoft.Authorization/roleAssignments/write`:

```bash
ROLE_ASSIGNMENT_ID="$(python - <<'PY'
import uuid
print(uuid.uuid4())
PY
)"

az rest   --method put   --url "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Authorization/roleAssignments/$ROLE_ASSIGNMENT_ID?api-version=2022-04-01"   --body "{
    \"properties\": {
      \"roleDefinitionId\": \"/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Authorization/roleDefinitions/$UAA_ROLE_ID\",
      \"principalId\": \"$BACKEND_SP_OBJECT_ID\",
      \"principalType\": \"ServicePrincipal\"
    }
  }"
```

Verify:

```bash
az role assignment list   --assignee "$BACKEND_SP_OBJECT_ID"   --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"   --role "$UAA_ROLE_ID"   --output table
```

## Frontend — storage data-plane permission missing

The frontend production workflow successfully authenticated to Azure and reached the blob upload step. The upload failed because its OIDC identity did not have Microsoft Entra blob data-plane write permission.

Required permission:

- **Storage Blob Data Contributor**
- Scope: `st16resumeweb` only
- Authentication remains `--auth-mode login`

No storage key, SAS token, connection string, client secret, or publish profile is introduced.

### Command-line correction

Use the frontend production OIDC service principal object ID:

```bash
SUBSCRIPTION_ID="aab5f649-b686-4f86-95cc-aa72ae71f03b"
RESOURCE_GROUP="rg-sixteen-resume-prod"
FRONTEND_STORAGE_ACCOUNT="st16resumeweb"

FRONTEND_SP_OBJECT_ID="$(
  az ad sp list     --display-name "sixteen-resume-frontend-github-actions"     --query "[0].id"     --output tsv
)"

test -n "$FRONTEND_SP_OBJECT_ID"

STORAGE_SCOPE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$FRONTEND_STORAGE_ACCOUNT"

az role assignment create   --assignee-object-id "$FRONTEND_SP_OBJECT_ID"   --assignee-principal-type ServicePrincipal   --role "Storage Blob Data Contributor"   --scope "$STORAGE_SCOPE"
```

Verify:

```bash
az role assignment list   --assignee "$FRONTEND_SP_OBJECT_ID"   --scope "$STORAGE_SCOPE"   --role "Storage Blob Data Contributor"   --output table
```

## Verification gate

Phase 3 remains **BLOCKED** until fresh production evidence proves:

1. Backend OIDC authentication succeeds.
2. Backend ARM validation/deployment creates the approved role assignments.
3. Backend Function deployment reaches the existing HTTPS `GET /api/visitors` readiness check.
4. Frontend OIDC authentication succeeds.
5. Frontend upload to `$web` succeeds with `--auth-mode login`.
6. Public HTTPS verification succeeds.
7. No storage keys, SAS tokens, client secrets, or publish profiles are used.

This remediation changes only Azure RBAC assignments required by the existing implementation.


## Phase 3 blocker correction — Cosmos Table endpoint — 2026-10-07

The deployed Function App was configured with the Cosmos DB **document endpoint** while the visitor counter uses the Azure Tables SDK against the Cosmos DB Table API. This caused the production visitor endpoint to return `503 DEPENDENCY_UNAVAILABLE` and intermittently time out.

The backend ARM template now wires `COSMOS_ENDPOINT` from the Cosmos account's `tableEndpoint` property and aligns the native Cosmos Table RBAC resource API version with the documented `2023-04-15` contract.

The backend deployment workflow now verifies, before HTTP readiness, that:

- the current Function App system-assigned identity owns exactly one Cosmos DB Built-in Data Contributor Table role assignment at the Cosmos account scope;
- the Cosmos account exposes a distinct Table endpoint;
- the production runtime is therefore targeting the Table API rather than the NoSQL document endpoint.

No frontend application code, API contract, browser/Cosmos boundary, or authentication model changed.

**Phase 3 blocker status:** backend Cosmos endpoint wiring corrected; fresh production deployment and HTTP/persistence evidence required before the blocker can be marked resolved.
