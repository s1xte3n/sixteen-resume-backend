# Phase 5 — Secrets & Credential Management

## Security baseline

**No long-lived Azure credential is part of the approved architecture.**

GitHub Actions authenticates to Azure through workload identity federation/OIDC. The Function authenticates to Cosmos DB for Table through its system-assigned managed identity and native RBAC.

## Secret/credential inventory

| ID | Name/reference | Type | Consumer | Storage | Injection | Lifetime | Rotation | Managed identity/OIDC eliminates it? | Logs | Commit |
|---|---|---|---|---|---|---|---|---|---|---|
| SEC-001 | AZURE_CLIENT_ID | OIDC identifier | GitHub Actions | GitHub production environment protected secret in current workflow | azure/login OIDC input | Federated-token based; identifier persists | Update when deployment identity changes | OIDC removes client secret, not the identifier | Never echo unnecessarily | Never in source values |
| SEC-002 | AZURE_TENANT_ID | OIDC identifier | GitHub Actions | GitHub production environment protected secret in current workflow | azure/login OIDC input | Persistent identifier | Change only if tenant changes | OIDC removes client secret | Never echo unnecessarily | Never commit as secret value |
| SEC-003 | AZURE_SUBSCRIPTION_ID | OIDC identifier | GitHub Actions | GitHub production environment protected secret in current workflow | azure/login OIDC input | Persistent identifier | Change only if subscription changes | OIDC removes client secret | Never echo unnecessarily | Never commit as secret value |
| SEC-004 | Azure client secret | Long-lived credential | None | N/A | None | N/A | N/A | **Yes** | Never | Must not exist |
| SEC-005 | COSMOS_CONNECTION_STRING | Database credential | None in production | N/A | None | N/A | N/A | **Yes** | Never | Must not exist |
| SEC-006 | COSMOS_ACCOUNT_KEY | Database credential | None | N/A | None | N/A | N/A | **Yes** | Never | Must not exist |
| SEC-007 | AZURE_STORAGE_CONNECTION_STRING | Storage credential | None in production | N/A | None | N/A | N/A | **Yes** | Never | Must not exist |
| SEC-008 | Function platform-managed secrets | Platform credential | Azure Functions | Azure-managed platform store | Platform-managed | Provider-managed | Provider-managed | Not applicable | Never expose | Never |
| SEC-009 | Local Azurite connection string | Local test credential/config | Local backend | Untracked local.settings.json | Process environment | Local only | Replace if local setup changes | Not applicable | Never publish | Never commit actual secret-bearing local file |

### Important classification

The OIDC values are identifiers rather than passwords/keys. The current workflows intentionally store them as GitHub Environment Secrets because that is the approved protected input mechanism. They must never be treated as evidence that a client secret exists.

## Backend runtime credential flow

Function App system-assigned managed identity
→ Azure RBAC / Cosmos Table native role
→ Table API
→ counter state

No Cosmos key, connection string, SAS token, or browser credential is used.

## Frontend deployment credential flow

GitHub Actions OIDC token
→ Microsoft Entra workload identity federation
→ dedicated frontend user-assigned managed identity
→ Storage Blob Data Contributor on frontend Storage account
→ upload `$web`

No Storage key or connection string is used.

## Backend deployment credential flow

GitHub Actions OIDC token
→ Microsoft Entra workload identity federation
→ dedicated backend deployment identity
→ scoped production resource-group deployment permissions
→ ARM deployment

The backend deployment identity requires the approved deployment permissions because ARM creates managed-identity role assignments. Owner/subscription-wide permissions are not authorized.

## Exposure rules

- No secret in browser JavaScript, HTML, CSS, Postman environments, fixtures, ARM parameter files, logs, API responses, or error messages.
- No credential in Git history.
- Do not print GitHub secrets.
- Do not upload secret-bearing files as workflow artifacts.
- If a credential is exposed, revoke/replace it and treat repository-history cleanup as separate remediation.

## Rotation/revocation

For OIDC identity replacement:
1. Create/approve replacement identity.
2. Create exact federated credential.
3. Assign required scoped RBAC.
4. Update protected GitHub environment identifier.
5. Run OIDC verification.
6. Deploy and verify.
7. Remove superseded identity/RBAC only after replacement is proven.
