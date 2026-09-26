# Azure ARM Infrastructure

## Scope

This directory contains the source-controlled ARM infrastructure for the resolved Azure core resources of the Cloud Resume Challenge.

The template provisions:

- Azure Storage static website hosting for the frontend.
- Azure Functions Linux Consumption hosting.
- Azure Functions host storage.
- Azure Cosmos DB for Table API in serverless capacity.
- The single `VisitorCounter` table.
- Function managed identity with Cosmos DB for Table native data-plane contributor access scoped to the counter table.
- Production Function CORS restricted to the approved frontend HTTPS origin.

## Cost and hosting lifecycle

The approved MVP recurring Azure/cloud cost ceiling is **R100/month**. The previous **USD $40/month** wording is obsolete and must not be used for the current MVP baseline. **R100/month is the authoritative recurring ceiling**, with lower cost preferred where practical.

The approved MVP ARM architecture uses **Azure Functions Linux Consumption** hosting (`Y1` / Dynamic). This is an intentional MVP architecture decision. Microsoft has announced that hosting Function Apps on Linux in the Consumption plan will retire on **30 September 2028**; Linux Consumption is no longer receiving new features or language versions, and Microsoft directs affected apps toward **Flex Consumption**. The MVP can therefore proceed with Linux Consumption as the current approved hosting model while treating migration to Flex Consumption as a lifecycle requirement before retirement.

The retirement is a lifecycle constraint, not a Phase 7.3 blocker. The production cost gate remains **<= R100/month** for the complete deployed MVP.

The template does **not** provision the public HTTPS/CDN delivery layer yet. ADR-006 deliberately leaves the exact Azure edge service/SKU as an implementation-time selection. Selecting one without validating availability, lifecycle, FreeDNS hostname compatibility, Storage origin compatibility, IaC support, and the R100/month ceiling would violate the project source of truth.

## Source-of-truth alignment

- Architecture: `s1xte3n/sixteen-resume-frontend/docs/architecture/INFRASTRUCTURE.md`
- Security: `s1xte3n/sixteen-resume-frontend/docs/architecture/SECURITY-ARCHITECTURE.md`
- ADR: `ADR-005` for identity and least privilege; `ADR-006` for HTTPS/CDN selection.
- Requirements: `REQ-AZ-012`, `REQ-AZ-013`, `REQ-AZ-DEV-001`.
- Verification: `T-012-P`, `T-012-N`, `T-IAC-001`, `T-SEC-003`.

## Deployment boundary

Deploy at **resource-group scope**. The resource group must already exist and must be the approved production resource group.

The template deliberately does not create a resource group.

## Prerequisites

1. Azure CLI authenticated to the approved subscription.
2. An existing production resource group.
3. Current Azure resource availability validated for East US.
4. A globally unique set of resource names.
5. The approved production frontend HTTPS origin for `corsAllowedOrigin`.

## Validate

Run:

```bash
az deployment group validate \
  --resource-group "<RESOURCE_GROUP>" \
  --template-file infra/azure/azuredeploy.json \
  --parameters \
    frontendStorageAccountName="<FRONTEND_STORAGE_ACCOUNT>" \
    functionStorageAccountName="<FUNCTION_STORAGE_ACCOUNT>" \
    functionPlanName="sixteen-resume-functions" \
    functionAppName="<FUNCTION_APP_NAME>" \
    cosmosAccountName="<COSMOS_ACCOUNT_NAME>" \
    corsAllowedOrigin="https://<APPROVED_PUBLIC_HOSTNAME>"
```

A real Azure validation requires an authenticated Azure context and an existing resource group; source-only JSON parsing is not equivalent to Azure deployment validation.

## Deploy

Only after the validation gate and the unresolved HTTPS/CDN service-selection gate are satisfied:

```bash
az deployment group create \
  --resource-group "<RESOURCE_GROUP>" \
  --template-file infra/azure/azuredeploy.json \
  --parameters \
    frontendStorageAccountName="<FRONTEND_STORAGE_ACCOUNT>" \
    functionStorageAccountName="<FUNCTION_STORAGE_ACCOUNT>" \
    functionPlanName="sixteen-resume-functions" \
    functionAppName="<FUNCTION_APP_NAME>" \
    cosmosAccountName="<COSMOS_ACCOUNT_NAME>" \
    corsAllowedOrigin="https://<APPROVED_PUBLIC_HOSTNAME>" \
  --name "sixteen-resume-core"
```

The deployment outputs include the frontend Storage endpoint, Function URL, Cosmos endpoint, and Function principal ID.

## Security notes

- No Azure credential is committed.
- The Function uses `DefaultAzureCredential` for Cosmos DB.
- Cosmos local/key authentication is disabled.
- The Cosmos built-in Table Data Contributor role is used for the Function identity and scoped to the single counter table.
- The Functions platform host-storage connection is generated at deployment time from Azure Storage keys because this project remains on the approved classic Consumption plan. The value is not hardcoded in source and is not exported as an output.
- The frontend deployment identity is not created by this template; it is managed by the frontend repository's OIDC setup.
- The backend GitHub OIDC identity is a separate delivery/identity concern and must be provisioned with the backend CI/CD work.

## Known implementation gate

The template represents the resolved core infrastructure. Full `REQ-AZ-012` / `T-IAC-001` acceptance remains blocked until:

1. Azure validates and deploys the template successfully.
2. Function managed identity can authenticate to the Cosmos Table API.
3. The visitor API smoke/contract tests pass against the deployed Function.
4. The exact Azure HTTPS/CDN service is selected and validated under ADR-006.
5. FreeDNS hostname and HTTPS evidence are available.
6. The complete deployed cost is proven to remain <= R100/month.

The ARM template is therefore **implemented but not production-accepted**.
