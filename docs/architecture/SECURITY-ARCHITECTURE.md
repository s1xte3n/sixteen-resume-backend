# Security Architecture

## CI/CD identity
GitHub Actions authenticates with workload identity federation. No Azure client secret is required.

## RBAC
- Backend deployment principal: User Access Administrator or Role Based Access Control Administrator at `rg-sixteen-resume-prod`.
- Frontend deployment principal: Storage Blob Data Contributor on `st16resumeweb`.
- Function managed identity: storage/Cosmos data roles only.

Contributor alone cannot create `Microsoft.Authorization/roleAssignments`; therefore the backend deployment identity needs scoped authorization-management permission.

## Storage
- TLS 1.2 minimum.
- Secure transfer required.
- Function/deployment storage has anonymous access disabled and shared-key access disabled.
- Frontend `$web` is intentionally public because static website content is anonymous.

## Public edge
The custom hostname must terminate HTTPS at Azure Front Door Standard/Premium with a Microsoft-managed certificate and HTTP-to-HTTPS redirect.


## Phase 3 blocker correction — current

The backend deployment service principal is the recreated GitHub OIDC identity and is restricted to the production resource group with Contributor + User Access Administrator. The Function App itself uses its system-assigned managed identity for Cosmos DB for Table access; no client secret, account key, SAS token, or direct browser credential is introduced.
