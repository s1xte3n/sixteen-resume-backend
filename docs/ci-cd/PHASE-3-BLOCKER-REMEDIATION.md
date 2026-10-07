# Phase 3 Blocker Remediation — 2026-10-07

## Scope

This document records only Phase 3 delivery blockers. It does not change the approved API, frontend architecture, browser-to-Cosmos isolation, Flex Consumption hosting model, or deployment authority.

## Backend GitHub OIDC client

The recreated backend Microsoft Entra application client ID is:

`4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d`

The federated credential must be attached to the current application object and must exactly match the immutable GitHub production subject:

`repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`

Issuer:

`https://token.actions.githubusercontent.com`

Audience:

`api://AzureADTokenExchange`

The GitHub production environment secret `AZURE_CLIENT_ID` must contain that client ID.

## Backend deployment RBAC

The ARM template creates role assignments for the Function App system-assigned identity. Therefore the GitHub deployment service principal needs permission to create role assignments at the production resource-group scope.

For client ID `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d`, obtain the **service-principal object ID**, not the application object ID:

`az ad sp show --id "$BACKEND_APP_ID" --query id -o tsv`

Required deployment roles:

- Contributor on `rg-sixteen-resume-prod`
- User Access Administrator on `rg-sixteen-resume-prod`

These are deployment-authority permissions. They do not grant the Function App identity additional data-plane access.

## Frontend deployment verification

The frontend pipeline now separates Azure Storage deployment verification from public DNS/CDN verification. The Storage endpoint must prove the uploaded website is reachable before the custom hostname is considered.

## Remaining Phase 3 blocker

`https://sixteen-resume.mooo.com/` currently times out because the public edge path is incomplete.

The existing Azure Front Door profile/endpoint alone is insufficient. A complete path requires an origin group/origin, route, custom domain, DNS validation and HTTPS configuration.

The approved project cost ceiling must also be satisfied before any edge service is accepted for production.

## Evidence rule

No Phase 3 gate is marked passed from configuration alone. A fresh production GitHub Actions run must prove OIDC login, deployment, runtime readiness and the required public endpoint behavior.
