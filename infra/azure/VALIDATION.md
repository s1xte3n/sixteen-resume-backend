# Phase 7.3 — Azure IaC Validation Record

## Phase 0 Status

This document contains historical validation evidence for the superseded Linux Consumption/Y1 template. It must not be interpreted as current Azure acceptance evidence.

**Current approved hosting:** Azure Functions Flex Consumption (FC1), Linux, Functions v4, Python 3.12, serverless scale-to-zero, zero always-ready instances for MVP.

The previous deployment failed because `Microsoft.Web/serverfarms/sixteen-resume-functions` could not provision with subscription Y1 VM quota = 0. The requested quota increase to 1 was unsuccessful. No further Y1 quota request is authorized.

## Scope

This record covers validation of the approved Phase 7.3 Azure core infrastructure in infra/azure/azuredeploy.json.

It does not declare Phase 7 complete and does not claim live Azure deployment success without authenticated Azure evidence.

## Source/configuration validation

| Area | Status | Evidence |
|---|---|---|
| Azure Storage static website | PASS | ARM template + tests/test_arm_template.py |
| Azure Functions Linux Consumption (historical) | SUPERSEDED | Microsoft.Web/serverfarms, SKU Y1, tier Dynamic, Linux Function App |
| Cosmos DB Table API | PASS | EnableTable capability + table resource |
| Cosmos serverless capacity | PASS | EnableServerless capability |
| Managed identity | PASS | Function App system-assigned identity |
| Cosmos Table RBAC | PASS | Built-in Table Data Contributor role scoped to VisitorCounter table |
| Function application settings | PASS | Python 3.12, Functions v4, production table backend, Cosmos endpoint |
| Production CORS | PASS | Parameterized, non-wildcard origin |
| HTTPS | PASS for Function endpoint | httpsOnly=true |
| Static-site HTTPS/CDN | BLOCKED | Exact edge service remains pending ADR-006 implementation validation |
| Application Insights resource | NOT REQUIRED | Architecture requires diagnosable Function/platform logs but does not mandate a separate Application Insights resource |
| Runtime logging | PASS | Controlled visitor API failures are logged with request IDs and without exception details in public responses |
| Resource dependencies | PASS | Function depends on hosting plan, host storage, Cosmos account, and counter table |
| East US | PASS | Location parameter restricted to eastus |
| ARM parameters/outputs | PASS | Template defines deployment inputs and core outputs |
| Credential safety | PASS | No long-lived CI/Cosmos credential markers in template |
| Cost documentation | PASS | R100/month recurring Azure/cloud ceiling is authoritative |
| Linux Consumption lifecycle (historical) | SUPERSEDED | Retirement/migration rationale led to the approved Flex Consumption change |

## Test coverage added

tests/test_arm_template.py now verifies:

- approved East US location;
- explicit Linux Consumption Y1 / Dynamic hosting;
- Function resource dependency ordering;
- existing Storage, Cosmos, identity, CORS, RBAC, and credential-safety controls.

tests/test_visitors.py now verifies that controlled dependency and unexpected runtime failures are logged while exception details are not returned to the public API response.

## Live Azure validation

The following evidence remains required and is intentionally not claimed here:

1. az deployment group validate against the approved production resource group.
2. Successful resource-group deployment from the committed ARM template.
3. Runtime verification of Function managed identity access to the Cosmos Table API.
4. Deployed visitor API smoke/contract verification.
5. Exact HTTPS/CDN service selection and deployment.
6. FreeDNS hostname and HTTPS evidence.
7. Complete deployed cost evidence proving the recurring ceiling remains <= R100/month.
8. Successful CI/CD deployment evidence using the approved OIDC identities.

## Current Hosting Baseline

The project no longer uses Linux Consumption/Y1 as its current architecture. The current decision is Azure Functions Flex Consumption (FC1), Linux, Functions v4, Python 3.12, serverless scale-to-zero, and zero always-ready instances for the MVP.

Flex-specific ARM validation is a Phase 1 follow-up. The existing ARM tests and historical validation evidence apply only to the superseded template.

## Acceptance boundary

Phase 7.3 core IaC is implementation-ready but not production-accepted until the live Azure and edge-delivery evidence above is available.