# Phase 5 — Configuration Dependency Map

```
Approved requirements
      |
      v
Frozen architecture + API contract
      |
      +--> ARM parameters
      |      |
      |      +--> Resource group
      |      +--> East US
      |      +--> Storage accounts
      |      +--> Flex plan/App
      |      +--> Cosmos account/table
      |      +--> CORS origin
      |
      +--> GitHub production environment
      |      |
      |      +--> OIDC identifiers
      |      +--> Azure resource variables
      |      +--> hostname/edge variables
      |
      v
GitHub Actions OIDC
      |
      v
Azure deployment identity
      |
      v
ARM deployment
      |
      +--> Frontend Storage
      +--> Function App + system identity
      +--> Function host storage
      +--> Flex deployment storage
      +--> Cosmos Table
      |
      +--> RBAC role assignments
             |
             +--> Function identity -> Storage roles
             +--> Function identity -> Cosmos Table role
             +--> CI identity -> deployment permissions
             +--> Frontend identity -> Storage Blob Data Contributor
      |
      v
Function runtime
      |
      +--> identity-based host storage
      +--> Cosmos endpoint
      +--> VisitorCounter / VisitorCounter:Global
      |
      v
GET /api/visitors
      |
      v
Frontend same-origin JavaScript
      |
      +--> /api/visitors
      |
      v
HTTPS edge / DNS
      |
      v
PUBLIC_HOSTNAME
```

## Ordering constraints

1. Production resource group must exist before resource-group-scoped ARM deployment.
2. Azure/OIDC identity and required deployment RBAC must exist before CI can deploy.
3. Storage/Cosmos/Function resources must exist before their generated endpoints/identities can be recorded.
4. Function managed identity must exist before its data-plane role assignments can be verified.
5. Final public hostname/edge must exist before final CORS can be frozen.
6. Final CORS must exist before production browser/API acceptance.
7. Backend deployment must succeed before frontend end-to-end verification.
8. Public endpoint verification remains disabled until the approved edge/DNS path exists.
