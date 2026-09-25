from __future__ import annotations

import time
from typing import Any

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.core import MatchConditions
from azure.data.tables import TableClient, UpdateMode

from src.domain.errors import (
    VisitorCounterDependencyError,
    VisitorCounterTimeoutError,
)


class TableVisitorCounter:
    """Concurrency-safe visitor counter backed by Azure Cosmos DB Table API."""

    def __init__(
        self,
        table_client: TableClient,
        *,
        partition_key: str = "VisitorCounter",
        row_key: str = "Global",
        max_retries: int = 8,
        retry_delay_seconds: float = 0.01,
    ) -> None:
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be non-negative")

        self._table_client = table_client
        self._partition_key = partition_key
        self._row_key = row_key
        self._max_retries = max_retries
        self._retry_delay_seconds = retry_delay_seconds

    def increment(self) -> int:
        for attempt in range(self._max_retries):
            try:
                entity = self._table_client.get_entity(
                    partition_key=self._partition_key,
                    row_key=self._row_key,
                )
            except ResourceNotFoundError:
                try:
                    return self._create_initial_entity()
                except ResourceExistsError:
                    self._backoff(attempt)
                    continue
                except (ServiceRequestError, TimeoutError) as exc:
                    raise VisitorCounterTimeoutError(
                        "Visitor counter initialization timed out."
                    ) from exc
                except HttpResponseError as exc:
                    raise VisitorCounterDependencyError(
                        "Visitor counter initialization failed."
                    ) from exc
            except (ServiceRequestError, TimeoutError) as exc:
                raise VisitorCounterTimeoutError(
                    "Visitor counter read timed out."
                ) from exc
            except HttpResponseError as exc:
                raise VisitorCounterDependencyError(
                    "Visitor counter read failed."
                ) from exc

            count = _validated_count(entity.get("Count"))
            updated_entity = {
                "PartitionKey": self._partition_key,
                "RowKey": self._row_key,
                "Count": count + 1,
            }

            try:
                self._table_client.update_entity(
                    entity=updated_entity,
                    mode=UpdateMode.REPLACE,
                    etag=entity.metadata["etag"],
                    match_condition=MatchConditions.IfNotModified,
                )
                return count + 1
            except ResourceModifiedError:
                self._backoff(attempt)
                continue
            except (ServiceRequestError, TimeoutError) as exc:
                raise VisitorCounterTimeoutError(
                    "Visitor counter update timed out."
                ) from exc
            except HttpResponseError as exc:
                raise VisitorCounterDependencyError(
                    "Visitor counter update failed."
                ) from exc

        raise VisitorCounterDependencyError(
            "Visitor counter could not be updated after retrying concurrent conflicts."
        )

    def _create_initial_entity(self) -> int:
        self._table_client.create_entity(
            entity={
                "PartitionKey": self._partition_key,
                "RowKey": self._row_key,
                "Count": 1,
            }
        )
        return 1

    def _backoff(self, attempt: int) -> None:
        if self._retry_delay_seconds == 0:
            return
        time.sleep(self._retry_delay_seconds * (attempt + 1))


def _validated_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise VisitorCounterDependencyError(
            "Visitor counter state is invalid."
        )
    return value
