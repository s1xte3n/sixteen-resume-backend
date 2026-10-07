# Phase 3 Gate Remediation

## Current Phase 3 blockers

1. **Backend OIDC client binding is stale.** The backend GitHub Actions app registration was recreated with client ID `e3f56077-0aae-4a90-bde3-d0c0ef2a35e0`, but production run #153 still receives `AADSTS700016`. The workflow already presents the correct immutable subject, so the remaining failure is the protected GitHub `production/AZURE_CLIENT_ID` value still referencing the deleted application.
2. **Backend deployment authorization must be complete.** The recreated backend service principal has User Access Administrator at the resource-group scope, but it also needs the approved deployment role at that scope. User Access Administrator alone is not the backend deployment role.
3. **Frontend OIDC is resolved.** Frontend production run #33 authenticated successfully with OIDC and uploaded the three static assets using Microsoft Entra authorization.
4. **Frontend public HTTPS routing is unresolved.** Run #33 fails only at `https://sixteen-resume.mooo.com/` with curl error 28 after Storage upload succeeds. This is a DNS/HTTPS delivery-layer blocker, not a frontend source or OIDC defect.

## Required remediation

### Backend GitHub environment

Set the backend `production` environment secret `AZURE_CLIENT_ID` to `e3f56077-0aae-4a90-bde3-d0c0ef2a35e0`.

Keep `AZURE_TENANT_ID=936720d3-5742-4aa8-a632-b7731b0f24ff` and `AZURE_SUBSCRIPTION_ID=aab5f649-b686-4f86-95cc-aa72ae71f03b`.

The Azure federated credential must remain bound to `repo:s1xte3n@39813590/sixteen-resume-backend@1373839879:environment:production`.

### Backend deployment RBAC

The backend deployment service principal must have `Contributor` and `User Access Administrator` at `rg-sixteen-resume-prod`. Do not grant Owner or subscription-wide permissions as a workaround.

### Frontend public endpoint

Do not weaken or remove the existing HTTPS smoke test. Verify that `sixteen-resume.mooo.com` resolves publicly, targets the approved HTTPS/CDN delivery endpoint, has a valid certificate, routes to the Azure Storage static website for `st16resumeweb`, and returns the deployed `index.html`.

If the approved edge/CDN resource has not yet been provisioned, that is the remaining Phase 3 infrastructure blocker. Do not replace HTTPS with the Storage origin URL merely to make CI green.

## Verification evidence

- Backend production workflow authenticates with the recreated client ID.
- Backend ARM validation/deployment completes.
- Backend Function package deployment and `GET /api/visitors` readiness succeed.
- Frontend production workflow authenticates and uploads successfully.
- `https://sixteen-resume.mooo.com/` passes the existing smoke test.
- No secrets, storage keys, client secrets, direct Cosmos access, or alternate deployment paths are introduced.

## Gate status

**BLOCKED — remaining external blockers are backend GitHub environment client-ID rebinding, backend deployment-role verification, and frontend DNS/HTTPS delivery readiness.**
