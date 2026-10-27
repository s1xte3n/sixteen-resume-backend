# Architecture Decision Record: Remove Azure Front Door

- **Status:** Accepted — removal planned; Azure resources have not been deleted by this record
- **Decision date:** 2026-10-27
- **Decision owner:** Project owner
- **Scope:** Azure Cloud Resume Challenge
- **Related repositories:** [Backend](https://github.com/s1xte3n/sixteen-resume-backend) · [Frontend](https://github.com/s1xte3n/sixteen-resume-frontend)

## Context

The project has a strict target Azure budget of **R100 per month**. The project owner reported an Azure charge of R200 and identified Front Door as a cost concern. Front Door can incur charges even when traffic is low, so retaining it is not justified unless a confirmed requirement depends on it.

## Decision

Remove Azure Front Door from the project architecture and avoid recreating it as part of deployment.

The project will retain the Azure Storage static website and the existing backend components (Azure Functions and Cosmos DB) unless a separate approved decision changes them. Front Door removal must not be treated as already completed: Azure resources and dependencies must be checked, migrated as needed, and the profile deleted through an approved operational change.

## Consequences and constraints

- Reduce the risk of recurring Front Door charges and help keep costs within the R100/month target; this target is not a guaranteed Azure spending cap.
- The Azure Storage static website endpoint can continue to serve the frontend.
- The Storage static website endpoint does not itself provide HTTPS for a custom domain. Before removing Front Door, confirm whether the project requires a custom domain and select a supported, affordable HTTPS option if it does.
- Review DNS records, custom-domain/TLS configuration, CDN/cache settings, deployment workflows, infrastructure-as-code templates, environment variables, and documentation for Front Door references or dependencies.
- Update frontend configuration only if the frontend calls a Front Door URL or relies on its routing/caching behavior.
- Update backend configuration and infrastructure only where Front Door is explicitly declared or referenced; do not remove Azure Functions, Cosmos DB, or unrelated resources as part of this decision.
- Verify the visitor counter and all frontend-to-API flows after the routing change.
- Keep secrets out of source control.

## Implementation and verification checklist

- [ ] Inventory Front Door resources, SKU, endpoints, custom domains, routes, origin groups, WAF policies, and current monthly cost.
- [ ] Identify whether the frontend uses a custom domain; decide on the post-Front-Door HTTPS and DNS approach before changing DNS.
- [ ] Search both repositories and Azure IaC/deployment configuration for Front Door resource declarations, endpoint URLs, purge steps, configuration, and documentation.
- [ ] Update IaC and CI/CD workflows so Front Door is not provisioned or managed.
- [ ] Deploy and verify the frontend and visitor-counter API using the replacement routing configuration.
- [ ] Confirm HTTPS, DNS resolution, API CORS/origin settings, cache behavior, and error handling.
- [ ] Delete the Front Door profile and associated resources only after dependencies are migrated and verified.
- [ ] Check Azure Cost Analysis after deletion to confirm Front Door charges stop; review residual or unrelated charges.
- [ ] Update the architecture, requirements, interface contract, environment/secret inventory, test strategy, and operational runbook wherever they reference Front Door.

## Out of scope

This decision does not authorize deleting the Storage account, Azure Functions, Cosmos DB, DNS zone, custom domain, or other Azure resources unless a dependency review confirms a specific change is required.

## Decision rationale

Cost control takes precedence over optional global edge routing for this low-traffic resume project. HTTPS, static-site availability, visitor-counter functionality, security, and reproducible deployment remain requirements to validate during implementation.

## Backend repository responsibilities

Inspect infrastructure definitions, deployment workflows, API configuration, CORS/origin allowlists, and any Front Door dependencies. Preserve Azure Functions and Cosmos DB unless they are explicitly tied to Front Door. Update and test only the configuration affected by the routing change.
