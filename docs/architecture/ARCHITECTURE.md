# Architecture

## Status
**Phase 3 blocker correction in progress.** The application/data architecture is frozen, but the production edge architecture is not currently feasible under the hard R100/month recurring Azure/cloud ceiling. Backend OIDC/RBAC identity alignment is also not yet proven for the latest recreated service principal.

## System
- Frontend: Azure Storage static website `st16resumeweb`.
- Public frontend ingress: **approved capability only** — Azure-managed HTTPS/CDN edge is required, but no production SKU is currently approved because Azure Front Door Standard conflicts with the R100/month ceiling.
- API: Azure Functions Flex Consumption, Linux, Python 3.12, `func-sixteen-resume`.
- Function host storage: `st16resumefunc`.
- Function deployment storage: `st16resumedeploy/function-deployments`.
- Visitor state: Azure Cosmos DB for Table API, serverless, table `VisitorCounter`.
- CI/CD: separate GitHub repositories using Microsoft Entra OIDC.

## Required flows
Browser -> HTTPS Front Door -> Storage static website.
Browser -> HTTPS Function API -> Cosmos Table.

## Phase 3 Feasibility Gate

The frontend edge must not be considered implementation-ready until the selected delivery service simultaneously satisfies Azure Storage static website origin compatibility, public-hostname HTTPS, current service lifecycle, source-controlled provisioning, and the hard R100/month recurring Azure/cloud ceiling. The temporary Front Door resource is diagnostic only.

## Security boundaries
- Public browser traffic terminates at Front Door over HTTPS.
- Function accesses Azure data through its managed identity.
- GitHub Actions uses federated identities; no client secrets or storage keys are stored in source control.
