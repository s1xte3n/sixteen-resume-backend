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


def resources(template: dict, resource_type: str) -> list[dict]:
    return [r for r in template["resources"] if r["type"] == resource_type]


def app_settings(function: dict) -> dict[str, str]:
    return {
        item["name"]: item["value"]
        for item in function["properties"]["siteConfig"]["appSettings"]
    }


def test_arm_template_is_valid_json_and_has_core_resources() -> None:
    template = load_template()
    types = resource_types(template)

    assert template["contentVersion"] == "1.0.0.0"
    assert "Microsoft.Storage/storageAccounts" in types
    assert "Microsoft.Storage/storageAccounts/blobServices" in types
    assert "Microsoft.Storage/storageAccounts/blobServices/containers" in types
    assert "Microsoft.Web/serverfarms" in types
    assert "Microsoft.Web/sites" in types
    assert "Microsoft.DocumentDB/databaseAccounts" in types
    assert "Microsoft.DocumentDB/databaseAccounts/tables" in types
    assert "Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments" in types
    assert "Microsoft.Authorization/roleAssignments" in types


def test_deployment_region_is_restricted_to_approved_east_us() -> None:
    template = load_template()
    location = template["parameters"]["location"]

    assert location["defaultValue"] == "eastus"
    assert location["allowedValues"] == ["eastus"]


def test_flex_consumption_fc1_linux_plan_is_explicitly_configured() -> None:
    template = load_template()
    plans = resources(template, "Microsoft.Web/serverfarms")

    assert len(plans) == 1

    plan = plans[0]
    assert plan["sku"]["name"] == "FC1"
    assert plan["sku"]["tier"] == "FlexConsumption"
    assert plan["kind"] == "functionapp"
    assert plan["properties"]["reserved"] is True

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert '"Y1"' not in template_text
    assert '"Dynamic"' not in template_text
    assert "computeMode" not in plan["properties"]


def test_flex_function_app_uses_function_app_config_for_runtime_scale_and_deployment() -> None:
    template = load_template()
    apps = resources(template, "Microsoft.Web/sites")

    assert len(apps) == 1

    function = apps[0]
    config = function["properties"]["functionAppConfig"]

    assert function["kind"] == "functionapp,linux"
    assert function["identity"]["type"] == "SystemAssigned"
    assert config["runtime"] == {"name": "python", "version": "3.12"}

    deployment = config["deployment"]["storage"]
    assert deployment["type"] == "blobContainer"
    assert deployment["authentication"]["type"] == "SystemAssignedIdentity"
    assert "deploymentStorageContainerName" in deployment["value"]
    assert config["scaleAndConcurrency"]["alwaysReady"] == []
    assert config["scaleAndConcurrency"]["instanceMemoryMB"] == 512
    assert config["scaleAndConcurrency"]["maximumInstanceCount"] == 1
    assert "triggers" not in config["scaleAndConcurrency"]


def test_deployment_storage_is_private_and_separate_from_runtime_storage() -> None:
    template = load_template()

    containers = resources(
        template,
        "Microsoft.Storage/storageAccounts/blobServices/containers",
    )
    assert len(containers) == 1
    assert containers[0]["properties"]["publicAccess"] == "None"
    assert "deploymentStorageAccountName" in containers[0]["name"]

    function = resources(template, "Microsoft.Web/sites")[0]
    deployment_value = function["properties"]["functionAppConfig"]["deployment"]["storage"]["value"]

    assert "deploymentStorageAccountName" in deployment_value
    assert "deploymentStorageContainerName" in deployment_value
    assert "SystemAssignedIdentity" in json.dumps(
        function["properties"]["functionAppConfig"]["deployment"]
    )


def test_runtime_storage_uses_identity_based_configuration() -> None:
    template = load_template()
    function = resources(template, "Microsoft.Web/sites")[0]
    settings = app_settings(function)

    assert "AzureWebJobsStorage__accountName" in settings
    assert "AzureWebJobsStorage" not in settings
    assert "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING" not in settings
    assert "WEBSITE_CONTENTSHARE" not in settings
    assert "WEBSITE_RUN_FROM_PACKAGE" not in settings
    assert "functionStorageAccountName" in settings["AzureWebJobsStorage__accountName"]


def test_runtime_and_deployment_storage_disable_shared_key_access() -> None:
    template = load_template()
    accounts = {
        r["name"]: r
        for r in resources(template, "Microsoft.Storage/storageAccounts")
    }

    runtime = accounts["[parameters('functionStorageAccountName')]"]
    deployment = accounts["[parameters('deploymentStorageAccountName')]"]

    assert runtime["properties"]["allowSharedKeyAccess"] is False
    assert runtime["properties"]["defaultToOAuthAuthentication"] is True
    assert deployment["properties"]["allowSharedKeyAccess"] is False
    assert deployment["properties"]["defaultToOAuthAuthentication"] is True


def test_frontend_storage_is_static_website_storage() -> None:
    template = load_template()
    static_website_resources = resources(
        template,
        "Microsoft.Storage/storageAccounts/blobServices",
    )

    frontend = next(
        resource
        for resource in static_website_resources
        if "frontendStorageAccountName" in resource["name"]
    )
    static_website = frontend["properties"]["staticWebsite"]

    assert static_website["enabled"] is True

    frontend_account = next(
        resource
        for resource in resources(template, "Microsoft.Storage/storageAccounts")
        if "frontendStorageAccountName" in resource["name"]
    )
    assert frontend_account["properties"]["allowBlobPublicAccess"] is True
    assert static_website["indexDocument"] == "index.html"
    assert static_website["errorDocument404Path"] == "404.html"


def test_cosmos_account_is_table_serverless_and_key_auth_disabled() -> None:
    template = load_template()
    accounts = resources(template, "Microsoft.DocumentDB/databaseAccounts")

    assert len(accounts) == 1
    properties = accounts[0]["properties"]
    capabilities = {item["name"] for item in properties["capabilities"]}

    assert "EnableTable" in capabilities
    assert "EnableServerless" in capabilities
    assert properties["disableLocalAuth"] is True


def test_function_uses_python_v4_and_production_table_backend() -> None:
    template = load_template()
    function = resources(template, "Microsoft.Web/sites")[0]
    settings = app_settings(function)

    assert function["properties"]["httpsOnly"] is True
    assert settings["FUNCTIONS_EXTENSION_VERSION"] == "~4"
    assert "FUNCTIONS_WORKER_RUNTIME" not in settings
    assert settings["APP_ENV"] == "production"
    assert settings["VISITOR_COUNTER_BACKEND"] == "table"
    assert settings["COSMOS_PARTITION_KEY"] == "VisitorCounter"
    assert settings["COSMOS_ROW_KEY"] == "Global"
    assert "COSMOS_CONNECTION_STRING" not in settings
    assert "COSMOS_ACCOUNT_KEY" not in settings


def test_function_cors_is_parameterized_and_not_wildcarded() -> None:
    template = load_template()
    function = resources(template, "Microsoft.Web/sites")[0]
    cors = function["properties"]["siteConfig"]["cors"]

    assert cors["allowedOrigins"] == ["[parameters('corsAllowedOrigin')]"]
    assert cors["supportCredentials"] is False
    assert "*" not in cors["allowedOrigins"]


def test_function_depends_on_flex_plan_storage_deployment_container_and_cosmos() -> None:
    template = load_template()
    function = resources(template, "Microsoft.Web/sites")[0]
    dependencies = set(function["dependsOn"])

    assert "[resourceId('Microsoft.Web/serverfarms', parameters('functionPlanName'))]" in dependencies
    assert "[resourceId('Microsoft.Storage/storageAccounts', parameters('functionStorageAccountName'))]" in dependencies
    assert "[resourceId('Microsoft.Storage/storageAccounts/blobServices/containers', parameters('deploymentStorageAccountName'), 'default', parameters('deploymentStorageContainerName'))]" in dependencies
    assert "[resourceId('Microsoft.DocumentDB/databaseAccounts', parameters('cosmosAccountName'))]" in dependencies
    assert "[resourceId('Microsoft.DocumentDB/databaseAccounts/tables', parameters('cosmosAccountName'), parameters('cosmosTableName'))]" in dependencies


def test_function_storage_rbac_is_least_privilege_for_flex_runtime_and_deployment() -> None:
    template = load_template()
    assignments = resources(template, "Microsoft.Authorization/roleAssignments")

    role_ids = {
        assignment["properties"]["roleDefinitionId"]
        for assignment in assignments
    }

    assert any("storageBlobDataOwnerRoleDefinitionId" in role for role in role_ids)
    assert any("storageTableDataContributorRoleDefinitionId" in role for role in role_ids)
    assert any("storageBlobDataContributorRoleDefinitionId" in role for role in role_ids)

    for assignment in assignments:
        assert assignment["properties"]["principalType"] == "ServicePrincipal"
        assert "reference(resourceId('Microsoft.Web/sites', parameters('functionAppName'))" in assignment["properties"]["principalId"]
        assert "reference(resourceId('Microsoft.Web/sites', parameters('functionAppName'))" not in assignment["name"]


def test_cosmos_role_assignment_uses_supported_table_rbac_scope() -> None:
    template = load_template()
    assignments = resources(
        template,
        "Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments",
    )

    assert len(assignments) == 1
    assignment = assignments[0]["properties"]

    assert "tableRoleDefinitions/00000000-0000-0000-0000-000000000002" in assignment[
        "roleDefinitionId"
    ]
    assert assignment["scope"] == "[resourceId('Microsoft.DocumentDB/databaseAccounts', parameters('cosmosAccountName'))]"
    assert "reference(resourceId('Microsoft.Web/sites', parameters('functionAppName'))" not in assignments[0]["name"]


def test_template_contains_no_legacy_consumption_or_long_lived_credentials() -> None:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    forbidden_markers = (
        "AZURE_CLIENT_SECRET",
        "AZURE_CREDENTIALS",
        "COSMOS_CONNECTION_STRING",
        "COSMOS_ACCOUNT_KEY",
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_STORAGE_SAS_TOKEN",
        "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING",
        "WEBSITE_CONTENTSHARE",
        "WEBSITE_RUN_FROM_PACKAGE",
        "FUNCTIONS_WORKER_RUNTIME",
    )

    for marker in forbidden_markers:
        assert marker not in template_text

    assert '"Y1"' not in template_text
    assert '"Dynamic"' not in template_text
