# Phase 3 Blocker Status

## Scope

This document records only Phase 3 deployment-verification blockers. It does not change the approved API contract, frontend architecture, hosting model, or credential model.

## Backend blocker — Flex host storage

**Observed failure:** backend CI failed the ARM regression test because the Function App template contained the required empty `AzureWebJobsStorage` setting in the deployed Flex configuration, while the repository regression test and deployment verification still asserted that the setting must be absent.

**Correction:**

- Retain identity-based `AzureWebJobsStorage__accountName`.
- Add `AzureWebJobsStorage=""` as the Flex host-storage compatibility setting.
- Grant the Function App system-assigned identity `Storage Queue Data Contributor` on the runtime Storage account.
- Update ARM structural tests to require the corrected configuration.
- Update production deployment verification to assert the same configuration.

The Queue role uses the Azure built-in role definition `974c5e8b-45b9-4653-ba55-5f855dd0fb88`.

## Frontend blocker — GitHub OIDC federation

**Observed failure:** the frontend production workflow presented the immutable GitHub production-environment subject:

`repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`

Azure returned `AADSTS700213` because no matching federated identity credential exists for that exact subject.

**Repository status:** no frontend workflow change is required. The deployment workflow already uses the protected `production` environment and GitHub's current immutable repository/environment subject.

**External prerequisite:** the dedicated frontend user-assigned managed identity must contain exactly:

- Issuer: `https://token.actions.githubusercontent.com`
- Subject: `repo:s1xte3n@39813590/sixteen-resume-frontend@1373840239:environment:production`
- Audience: `api://AzureADTokenExchange`

After the Azure credential is corrected, the existing OIDC verification workflow must pass before frontend production acceptance can proceed.

## Gate

Phase 3 remains **BLOCKED** until:

1. Backend CI passes the corrected Flex host-storage regression checks.
2. The backend production workflow successfully deploys and reaches the existing HTTPS `GET /api/visitors` readiness verification.
3. The frontend Azure federated credential is corrected externally and the existing OIDC verification workflow succeeds.

No Phase 4 redesign or unrelated feature work is included in this correction.
