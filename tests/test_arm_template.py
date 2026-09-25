from __future__ import annotations

import json
from pathlib import Path


TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1] / "infra" / "azure" / "azuredeploy.json"
)


def load_template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def resource_types(template: dict) -> set[str]:
    return {resource["type"] for resource in template["resources"]}


def test_arm_template_is_valid_json_and_has_core_resources() -> None:
    template = load_template()
    types = resource_types(template)

    assert template["contentVersion"] == "1.0.0.0"
    assert "Microsoft.Storage/storageAccounts" in types
    assert "Microsoft.Storage/storageAccounts/blobServices" in types
    assert "Microsoft.Web/serverfarms" in types
    assert "Microsoft.Web/sites" in types
    assert "Microsoft.DocumentDB/databaseAccounts" in types
    assert "Microsoft.DocumentDB/databaseAccounts/tables" in types
    assert "Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments" in types


def test_frontend_storage_is_static_website_storage() -> None:
    template = load_template()

    static_website_resources = [
        resource
        for resource in template["resources"]
        if resource["type"] == "Microsoft.Storage/storageAccounts/blobServices"
    ]

    assert len(static_website_resources) == 1

    static_website = static_website_resources[0]["properties"]["staticWebsite"]

    assert static_website["enabled"] is True
    assert static_website["indexDocument"] == "index.html"
    assert static_website["errorDocument404Path"] == "404.html"


def test_cosmos_account_is_table_serverless_and_key_auth_disabled() -> None:
    template = load_template()

    accounts = [
        resource
        for resource in template["resources"]
        if resource["type"] == "Microsoft.DocumentDB/databaseAccounts"
    ]

    assert len(accounts) == 1

    properties = accounts[0]["properties"]
    capabilities = {item["name"] for item in properties["capabilities"]}

    assert "EnableTable" in capabilities
    assert "EnableServerless" in capabilities
    assert properties["disableLocalAuth"] is True


def test_function_uses_python_and_production_table_backend() -> None:
    template = load_template()

    apps = [
        resource
        for resource in template["resources"]
        if resource["type"] == "Microsoft.Web/sites"
    ]

    assert len(apps) == 1

    function = apps[0]
    assert function["kind"] == "functionapp,linux"
    assert function["identity"]["type"] == "SystemAssigned"

    settings = {
        item["name"]: item["value"]
        for item in function["properties"]["siteConfig"]["appSettings"]
    }

    assert function["properties"]["httpsOnly"] is True
    assert function["properties"]["siteConfig"]["linuxFxVersion"] == "Python|3.12"
    assert settings["FUNCTIONS_EXTENSION_VERSION"] == "~4"
    assert settings["FUNCTIONS_WORKER_RUNTIME"] == "python"
    assert settings["APP_ENV"] == "production"
    assert settings["VISITOR_COUNTER_BACKEND"] == "table"
    assert settings["COSMOS_PARTITION_KEY"] == "VisitorCounter"
    assert settings["COSMOS_ROW_KEY"] == "Global"
    assert "COSMOS_CONNECTION_STRING" not in settings
    assert "COSMOS_ACCOUNT_KEY" not in settings


def test_function_cors_is_parameterized_and_not_wildcarded() -> None:
    template = load_template()

    apps = [
        resource
        for resource in template["resources"]
        if resource["type"] == "Microsoft.Web/sites"
    ]

    cors = apps[0]["properties"]["siteConfig"]["cors"]

    assert cors["allowedOrigins"] == ["[parameters('corsAllowedOrigin')]"]
    assert cors["supportCredentials"] is False
    assert "*" not in cors["allowedOrigins"]


def test_cosmos_role_assignment_is_table_scoped() -> None:
    template = load_template()

    assignments = [
        resource
        for resource in template["resources"]
        if resource["type"]
        == "Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments"
    ]

    assert len(assignments) == 1

    assignment = assignments[0]["properties"]

    assert "tableRoleDefinitions/00000000-0000-0000-0000-000000000002" in assignment[
        "roleDefinitionId"
    ]
    assert "/tables/" in assignment["scope"]


def test_template_contains_no_long_lived_ci_or_cosmos_credentials() -> None:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    forbidden_markers = (
        "AZURE_CLIENT_SECRET",
        "AZURE_CREDENTIALS",
        "COSMOS_CONNECTION_STRING",
        "COSMOS_ACCOUNT_KEY",
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_STORAGE_SAS_TOKEN",
    )

    for marker in forbidden_markers:
        assert marker not in template_text
