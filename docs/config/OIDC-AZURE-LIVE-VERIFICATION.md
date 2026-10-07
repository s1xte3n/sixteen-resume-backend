# Phase 5 — Controlled Live Backend OIDC/Azure Verification

## Purpose

This workflow is a manual, non-deploying verification of the **backend** GitHub Actions → Microsoft Entra OIDC trust and production deployment RBAC boundary.

Workflow: `.github/workflows/verify-azure-oidc.yml`

**Boundary correction:** frontend OIDC verification is a separate concern and must be performed from `s1xte3n/sixteen-resume-frontend`. Do not add frontend UAMI checks or frontend GitHub environment variables to the backend verification workflow.

## Backend identity model

The approved backend deployment identity is the Microsoft Entra application/service principal identified by the configured `AZURE_CLIENT_ID`.

It is **not** a user-assigned managed identity resource. Therefore:

- backend identity verification uses `az ad sp show` / `az ad app federated-credential list`;
- `az identity show --name sixteen-resume-backend-github ...` is not the correct verification command;
- the backend deployment identity is expected to have Contributor plus User Access Administrator at `rg-sixteen-resume-prod`.

The current live-reported backend client ID is `4e6b194b-4fd7-4d6f-8972-7c1a8d21eb8d` (reported 2026-10-07). Live Azure verification remains authoritative for its current existence, federated credential, and RBAC. The earlier `e3f56077-0aae-4a90-bde3-d0c0ef2a35e0` value is superseded and must not be used.

## Required protected production environment variables

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`

These are non-secret identifiers/configuration values. No Azure client secret is required.

## Backend acceptance checks

A successful run must prove:

1. GitHub production environment variables exist.
2. OIDC login succeeds.
3. Azure tenant and subscription match the configured identifiers.
4. Exactly one federated credential on the configured Entra application matches:
   - issuer: `https://token.actions.githubusercontent.com`
   - subject: `repo:s1xte3n/sixteen-resume-backend:environment:production`
   - audience: `api://AzureADTokenExchange`
5. The configured service principal has Contributor at `rg-sixteen-resume-prod`.
6. The configured service principal has User Access Administrator at `rg-sixteen-resume-prod`.

The workflow does not deploy ARM resources, change RBAC, or mutate production state.

## Frontend live verification

Frontend verification belongs to:

`s1xte3n/sixteen-resume-frontend/.github/workflows/verify-azure-oidc.yml`

The approved UAMI `sixteen-resume-frontend-github` now exists in `rg-sixteen-resume-prod` with client ID `2d19e037-cc57-462c-a950-862f9b8a80e6` and principal ID `200b60d9-b05a-4733-81f4-1053834de5c3`. Its production federated credential has been corrected to the exact approved subject and audience.

The frontend verifier must now be run only after GitHub production `AZURE_CLIENT_ID` is synchronized to `2d19e037-cc57-462c-a950-862f9b8a80e6` and its Storage Blob Data Contributor assignment is present.

## Controlled execution order

1. Use the backend verification workflow exactly as committed; do not mix frontend checks into it.
2. Verify the backend service principal directly with `az ad sp show --id <AZURE_CLIENT_ID>`.
3. Verify the backend app federated credential and production RG RBAC.
4. Provision the approved frontend UAMI if it is absent.
5. Configure its GitHub federated credential and Storage Blob Data Contributor role.
6. Configure the protected GitHub `production` environment variables in the frontend repository.
7. Run the frontend **Verify Azure OIDC** workflow.
8. Record run URL, commit SHA, conclusion, and failed/passed step evidence.
9. Do not add client secrets or broaden RBAC to make a failed verification pass.

## Current live status

**BLOCKED — frontend identity/federation corrected; frontend client-ID synchronization and Storage RBAC remain unverified**

Observed:

- Backend: the manual `az identity show` command targets the wrong Azure identity type. Verify the approved service principal/application instead.
- Frontend: `sixteen-resume-frontend-github` was not found in `rg-sixteen-resume-prod`.
- GitHub: the controlled verification attempt failed because `AZURE_FRONTEND_IDENTITY_NAME` was missing from the GitHub production environment. That variable belongs to the frontend verification path.
- No live OIDC pass is claimed until the repository-specific verification workflows succeed.

## Failure interpretation

- Missing backend `vars.*`: backend GitHub production environment configuration defect.
- Missing frontend `vars.*`: frontend GitHub production environment configuration defect.
- Azure login failure: OIDC federation/tenant/subscription/client-ID defect.
- Federated credential mismatch: Azure Entra federation defect.
- Backend Contributor missing: backend deployment identity RBAC defect.
- Backend User Access Administrator missing: backend deployment identity cannot create the approved managed-identity role assignments.
- Frontend UAMI missing: frontend identity provisioning defect.
- Frontend Storage Blob Data Contributor missing: frontend deployment authorization defect.

## Source-of-truth rule

This verification artifact records live evidence only. It does not redefine the API contract, runtime identity model, storage model, Cosmos model, or deployment architecture.


## Live correction — 2026-10-07

- Frontend UAMI: `sixteen-resume-frontend-github` exists in `rg-sixteen-resume-prod`.
- Frontend client ID: `2d19e037-cc57-462c-a950-862f9b8a80e6`.
- Frontend principal ID: `200b60d9-b05a-4733-81f4-1053834de5c3`.
- Federated credential subject: `repo:s1xte3n/sixteen-resume-frontend:environment:production`.
- Frontend GitHub `AZURE_FRONTEND_IDENTITY_NAME` is configured.
- Storage RBAC remains unverified because local `az role assignment` commands return `MissingSubscription`.
- Phase 5 remains NOT PASSED until protected client-ID synchronization and Storage RBAC are proven by the controlled frontend workflow.
