import json
import uuid
from urllib.parse import parse_qs, urlparse

import azure.functions as func

from function_app import counter, visitors


def _request(method="GET", url="http://localhost/api/visitors", headers=None, body=None):
    parsed_url = urlparse(url)
    params = {
        key: values[-1]
        for key, values in parse_qs(parsed_url.query).items()
    }

    return func.HttpRequest(
        method=method,
        body=body or b"",
        url=url,
        headers=headers or {},
        params=params,
        route_params={},
    )


def _response_json(response):
    return json.loads(response.get_body().decode("utf-8"))


def test_get_visitors_returns_200_and_increments():
    response = visitors(_request())
    payload = _response_json(response)

    assert response.status_code == 200
    assert isinstance(payload["count"], int)
    assert payload["count"] >= 1
    assert response.headers["X-Request-ID"]


def test_successful_get_returns_uuid_v4_request_id():
    response = visitors(_request())
    request_id = response.headers["X-Request-ID"]

    assert uuid.UUID(request_id).version == 4


def test_valid_client_request_id_is_preserved():
    request_id = str(uuid.uuid4())
    response = visitors(_request(headers={"X-Request-ID": request_id}))

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_client_request_id_returns_400_without_increment():
    before = counter.count
    response = visitors(_request(headers={"X-Request-ID": "not-a-uuid"}))
    payload = _response_json(response)

    assert response.status_code == 400
    assert payload["error"]["code"] == "BAD_REQUEST"
    assert counter.count == before


def test_non_v4_request_id_returns_400():
    request_id = str(uuid.uuid1())
    response = visitors(_request(headers={"X-Request-ID": request_id}))

    assert response.status_code == 400
    assert _response_json(response)["error"]["code"] == "BAD_REQUEST"


def test_unsupported_method_returns_405_without_increment():
    before = counter.count
    response = visitors(_request(method="POST"))

    assert response.status_code == 405
    assert _response_json(response)["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert counter.count == before


def test_query_parameters_return_400_without_increment():
    before = counter.count
    request = _request(url="http://localhost/api/visitors?foo=bar")

    response = visitors(request)

    assert response.status_code == 400
    assert _response_json(response)["error"]["code"] == "BAD_REQUEST"
    assert counter.count == before


def test_unsupported_content_type_returns_415_without_increment():
    before = counter.count
    response = visitors(_request(headers={"Content-Type": "text/plain"}))

    assert response.status_code == 415
    assert _response_json(response)["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert counter.count == before


def test_body_returns_400_without_increment():
    before = counter.count
    response = visitors(
        _request(
            headers={"Content-Type": "application/json"},
            body=b'{"unexpected":"value"}',
        )
    )

    assert response.status_code == 400
    assert _response_json(response)["error"]["code"] == "BAD_REQUEST"
    assert counter.count == before


def test_error_response_has_canonical_shape():
    response = visitors(_request(method="DELETE"))
    payload = _response_json(response)

    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert uuid.UUID(payload["error"]["requestId"]).version == 4


def test_concurrent_counter_operations_do_not_lose_increments():
    from concurrent.futures import ThreadPoolExecutor

    before = counter.count

    def invoke():
        return visitors(_request())

    with ThreadPoolExecutor(max_workers=16) as executor:
        responses = list(executor.map(lambda _: invoke(), range(32)))

    assert all(response.status_code == 200 for response in responses)
    counts = sorted(_response_json(response)["count"] for response in responses)

    assert counts == list(range(before + 1, before + 33))
    assert counter.count == before + 32

def test_dependency_unavailable_returns_503_without_increment(monkeypatch):
    from src.domain.errors import VisitorCounterDependencyError

    class FailingCounter:
        def increment(self):
            raise VisitorCounterDependencyError("dependency unavailable")

    monkeypatch.setattr("function_app.counter", FailingCounter())

    response = visitors(_request())
    payload = _response_json(response)

    assert response.status_code == 503
    assert payload["error"]["code"] == "DEPENDENCY_UNAVAILABLE"


def test_dependency_timeout_returns_504_without_increment(monkeypatch):
    from src.domain.errors import VisitorCounterTimeoutError

    class TimingOutCounter:
        def increment(self):
            raise VisitorCounterTimeoutError("dependency timeout")

    monkeypatch.setattr("function_app.counter", TimingOutCounter())

    response = visitors(_request())
    payload = _response_json(response)

    assert response.status_code == 504
    assert payload["error"]["code"] == "DEPENDENCY_TIMEOUT"
