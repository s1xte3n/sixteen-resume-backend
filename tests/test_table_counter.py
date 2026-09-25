import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from azure.data.tables import TableServiceClient

from src.infrastructure.table_counter import TableVisitorCounter


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_AZURITE_TESTS", "").lower() != "true",
    reason="Set RUN_AZURITE_TESTS=true to run the Azurite integration tests.",
)


def test_table_counter_initializes_and_persists():
    service = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
    table_name = f"VisitorCounter{uuid.uuid4().hex[:12]}"

    try:
        table = service.create_table_if_not_exists(table_name=table_name)
        counter = TableVisitorCounter(table)

        assert counter.increment() == 1

        # A fresh adapter instance must observe the persisted state rather than
        # resetting the counter in process memory.
        restarted_counter = TableVisitorCounter(table)
        assert restarted_counter.increment() == 2

        stored = table.get_entity(
            partition_key="VisitorCounter",
            row_key="Global",
        )
        assert stored["Count"] == 2
    finally:
        service.delete_table(table_name=table_name)
        service.close()


def test_table_counter_concurrent_increments_do_not_lose_updates():
    service = TableServiceClient.from_connection_string("UseDevelopmentStorage=true")
    table_name = f"VisitorCounter{uuid.uuid4().hex[:12]}"

    try:
        table = service.create_table_if_not_exists(table_name=table_name)

        def invoke():
            return TableVisitorCounter(table, retry_delay_seconds=0).increment()

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(lambda _: invoke(), range(32)))

        assert sorted(results) == list(range(1, 33))

        stored = table.get_entity(
            partition_key="VisitorCounter",
            row_key="Global",
        )
        assert stored["Count"] == 32
    finally:
        service.delete_table(table_name=table_name)
        service.close()



def test_table_counter_rejects_invalid_persisted_count():
    from src.domain.errors import VisitorCounterDependencyError

    class InvalidStateTable:
        def get_entity(self, *, partition_key, row_key):
            return {
                "PartitionKey": partition_key,
                "RowKey": row_key,
                "Count": -1,
                "etag": "ignored",
            }

    counter = TableVisitorCounter(InvalidStateTable(), retry_delay_seconds=0)

    with pytest.raises(VisitorCounterDependencyError):
        counter.increment()


def test_table_counter_maps_dependency_timeout_to_domain_error():
    from azure.core.exceptions import ServiceRequestError
    from src.domain.errors import VisitorCounterTimeoutError

    class TimeoutTable:
        def get_entity(self, *, partition_key, row_key):
            raise ServiceRequestError("timeout")

    counter = TableVisitorCounter(TimeoutTable(), retry_delay_seconds=0)

    with pytest.raises(VisitorCounterTimeoutError):
        counter.increment()
