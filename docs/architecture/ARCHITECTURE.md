# Architecture

## Status
Phase 3 architecture is implementation-aligned. Two production blockers remain: backend CI workload-identity authorization and public frontend HTTPS ingress.

## System
- Frontend: Azure Storage static website `st16resumeweb`.
- Public frontend ingress: Azure Front Door Standard/Premium with custom HTTPS domain `sixteen-resume.mooo.com`.
- API: Azure Functions Flex Consumption, Linux, Python 3.12, `func-sixteen-resume`.
- Function host storage: `st16resumefunc`.
- Function deployment storage: `st16resumedeploy/function-deployments`.
- Visitor state: Azure Cosmos DB for Table API, serverless, table `VisitorCounter`.
- CI/CD: separate GitHub repositories using Microsoft Entra OIDC.

## Required flows
Browser -> HTTPS Front Door -> Storage static website.
Browser -> HTTPS Function API -> Cosmos Table.

## Security boundaries
- Public browser traffic terminates at Front Door over HTTPS.
- Function accesses Azure data through its managed identity.
- GitHub Actions uses federated identities; no client secrets or storage keys are stored in source control.
