from __future__ import annotations

import os

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

from src.domain.visitor_counter import InMemoryVisitorCounter
from src.infrastructure.table_counter import TableVisitorCounter


_DEFAULT_TABLE_NAME = "VisitorCounter"
_DEFAULT_PARTITION_KEY = "VisitorCounter"
_DEFAULT_ROW_KEY = "Global"


def build_visitor_counter():
    backend = os.getenv("VISITOR_COUNTER_BACKEND", "memory").strip().lower()

    if backend == "memory":
        return InMemoryVisitorCounter()

    if backend != "table":
        raise ValueError(
            "VISITOR_COUNTER_BACKEND must be either 'memory' or 'table'."
        )

    table_name = os.getenv("AZURE_COSMOS_TABLE_NAME", _DEFAULT_TABLE_NAME)
    partition_key = os.getenv("COSMOS_PARTITION_KEY", _DEFAULT_PARTITION_KEY)
    row_key = os.getenv("COSMOS_ROW_KEY", _DEFAULT_ROW_KEY)
    app_env = os.getenv("APP_ENV", "local").strip().lower()

    if app_env == "local":
        connection_string = os.getenv("AZURE_TABLE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError(
                "AZURE_TABLE_CONNECTION_STRING is required for the local table backend."
            )

        service_client = TableServiceClient.from_connection_string(
            connection_string
        )
        table_client = service_client.create_table_if_not_exists(
            table_name=table_name
        )
    else:
        endpoint = os.getenv("COSMOS_ENDPOINT")
        if not endpoint:
            raise ValueError(
                "COSMOS_ENDPOINT is required for the Azure table backend."
            )

        service_client = TableServiceClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
            audience="https://cosmos.azure.com",
        )

        # Production infrastructure owns table creation. The runtime identity
        # only receives data-plane permissions needed to read/update entities.
        table_client = service_client.get_table_client(table_name)

    return TableVisitorCounter(
        table_client=table_client,
        partition_key=partition_key,
        row_key=row_key,
    )
