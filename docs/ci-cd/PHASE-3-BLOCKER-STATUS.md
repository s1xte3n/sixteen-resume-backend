# Phase 3 Blocker Status

## Scope

This document records only Phase 3 deployment-verification blockers. It does not change the approved API contract, hosting model, Flex Consumption architecture, or GitHub OIDC authentication model.

## Backend blocker — deployment identity recreation

The existing backend GitHub OIDC identity is an Entra application/service principal named `sixteen-resume`.

The required production GitHub subject is:

`repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`

The previous Azure deployment also established that the deployment identity could authenticate through OIDC but could not create the ARM template's required `Microsoft.Authorization/roleAssignments` resources.

### Approved correction

Recreate the backend deployment identity as:

- Entra application display name: `sixteen-resume`
- Authentication: GitHub Actions OIDC
- Issuer: `https://token.actions.githubusercontent.com`
- Subject: `repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`
- Audience: `api://AzureADTokenExchange`
- GitHub production environment: `production`
- Azure deployment scope: `rg-sixteen-resume-prod`

The recreated service principal must receive only the Azure permissions required by the approved ARM deployment. Do not introduce client secrets, publish profiles, or subscription-wide Owner access.

The GitHub `production` environment must be updated with the recreated `AZURE_CLIENT_ID`. `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` remain unchanged.

## Frontend blocker — deployment identity recreation

The frontend deployment identity remains a dedicated user-assigned managed identity.

Its federated credential must exactly match:

- Issuer: `https://token.actions.githubusercontent.com`
- Subject: `repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`
- Audience: `api://AzureADTokenExchange`

The frontend identity must retain only the approved storage data-plane access.

The GitHub `production` environment must be updated with the recreated identity's `AZURE_CLIENT_ID`. `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` remain unchanged.

## Verification gate

Phase 3 remains **BLOCKED** until:

1. Backend identity recreation and OIDC federation are verified.
2. Backend ARM deployment can create its required RBAC resources without broad privilege escalation.
3. Backend production deployment reaches the existing HTTPS `GET /api/visitors` readiness check.
4. Frontend identity recreation and exact immutable-subject federation are verified.
5. The existing frontend OIDC verification workflow succeeds.

No API contract, frontend architecture, storage model, CDN decision, or authentication mechanism is changed by this remediation.
