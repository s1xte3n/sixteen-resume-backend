# Phase 5 — Controlled Live Backend OIDC/Azure Verification

## Purpose

This workflow is a manual, non-deploying verification of the approved backend GitHub Actions → Microsoft Entra OIDC trust and production deployment RBAC boundary.

Workflow: `.github/workflows/verify-azure-oidc.yml`

## Required protected production environment variables

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`

These are non-secret identifiers/configuration values. No Azure client secret is required.

## Acceptance checks

A successful run must prove:

1. GitHub production environment variables exist.
2. OIDC login succeeds.
3. Azure tenant and subscription match the configured identifiers.
4. Exactly one federated credential matches:
   - issuer: `https://token.actions.githubusercontent.com`
   - subject: `repo:s1xte3n/sixteen-resume-backend:environment:production`
   - audience: `api://AzureADTokenExchange`
5. The deployment service principal has Contributor at `rg-sixteen-resume-prod`.
6. The deployment service principal has User Access Administrator at `rg-sixteen-resume-prod`.

The workflow does not deploy ARM resources, change RBAC, or mutate production state.

## Controlled execution

1. Merge the verification workflow through the normal protected PR path.
2. Open GitHub Actions for the backend repository.
3. Select **Verify Azure OIDC**.
4. Select **Run workflow** against `main`.
5. Confirm the protected `production` environment is used.
6. Record run URL, commit SHA, conclusion, and failed/passed step evidence.
7. Do not add a client secret or broaden RBAC to make a failed verification pass.

## Current status

**PENDING LIVE EVIDENCE.**

This environment cannot dispatch `workflow_dispatch` or inspect the Azure tenant directly. No live pass is claimed until the controlled GitHub Actions run succeeds.

## Failure interpretation

- Missing `vars.*`: GitHub production environment configuration defect.
- Azure login failure: OIDC federation/tenant/subscription/client-ID defect.
- Federated credential mismatch: Azure Entra federation defect.
- Contributor missing: deployment identity RBAC defect.
- User Access Administrator missing: deployment identity cannot create the approved managed-identity role assignments.
