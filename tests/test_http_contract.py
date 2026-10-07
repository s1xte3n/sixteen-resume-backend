import json
import os
import urllib.error
import urllib.request
import uuid

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_FUNCTION_HOST_TESTS", "").lower() != "true",
    reason="Set RUN_FUNCTION_HOST_TESTS=true to run HTTP contract tests against the local Functions host.",
)

BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071").rstrip("/")
VISITORS_URL = f"{BASE_URL}/api/visitors"


def _request(method="GET", url=VISITORS_URL, headers=None, body=None):
    request = urllib.request.Request(
        url=url,
        method=method,
        headers=headers or {},
        data=body,
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def _json(body):
    return json.loads(body.decode("utf-8"))


def test_http_get_returns_contract_response_and_increments():
    status_1, headers_1, body_1 = _request()
    status_2, headers_2, body_2 = _request()

    payload_1 = _json(body_1)
    payload_2 = _json(body_2)

    assert status_1 == 200
    assert status_2 == 200
    assert set(payload_1) == {"count"}
    assert set(payload_2) == {"count"}
    assert isinstance(payload_1["count"], int)
    assert isinstance(payload_2["count"], int)
    assert payload_2["count"] == payload_1["count"] + 1
    assert uuid.UUID(headers_1["X-Request-ID"]).version == 4
    assert uuid.UUID(headers_2["X-Request-ID"]).version == 4


def test_http_valid_request_id_is_preserved():
    request_id = str(uuid.uuid4())

    status, headers, body = _request(
        headers={"X-Request-ID": request_id},
    )

    assert status == 200
    assert headers["X-Request-ID"] == request_id
    assert set(_json(body)) == {"count"}


def test_http_invalid_request_id_returns_canonical_400_without_increment():
    status_before, _, body_before = _request()
    before = _json(body_before)["count"]

    status, headers, body = _request(
        headers={"X-Request-ID": "not-a-uuid"},
    )

    status_after, _, body_after = _request()
    after = _json(body_after)["count"]

    assert status_before == 200
    assert status == 400
    assert status_after == 200
    assert after == before + 1
    assert uuid.UUID(headers["X-Request-ID"]).version == 4

    payload = _json(body)
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert payload["error"]["code"] == "BAD_REQUEST"


def test_http_query_parameters_return_canonical_400_without_increment():
    status_before, _, body_before = _request()
    before = _json(body_before)["count"]

    status, _, body = _request(url=f"{VISITORS_URL}?foo=bar")

    status_after, _, body_after = _request()
    after = _json(body_after)["count"]

    assert status_before == 200
    assert status == 400
    assert status_after == 200
    assert after == before + 1

    payload = _json(body)
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert payload["error"]["code"] == "BAD_REQUEST"


def test_http_unsupported_method_returns_405_without_increment():
    status_before, _, body_before = _request()
    before = _json(body_before)["count"]

    status, _, body = _request(method="POST")

    status_after, _, body_after = _request()
    after = _json(body_after)["count"]

    assert status_before == 200
    assert status == 405
    assert status_after == 200
    assert after == before + 1

    payload = _json(body)
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert payload["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_http_body_returns_400_without_increment():
    status_before, _, body_before = _request()
    before = _json(body_before)["count"]

    status, _, body = _request(
        headers={"Content-Type": "application/json"},
        body=b'{"unexpected":"value"}',
    )

    status_after, _, body_after = _request()
    after = _json(body_after)["count"]

    assert status_before == 200
    assert status == 400
    assert status_after == 200
    assert after == before + 1

    payload = _json(body)
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert payload["error"]["code"] == "BAD_REQUEST"


def test_http_unsupported_content_type_returns_415_without_increment():
    status_before, _, body_before = _request()
    before = _json(body_before)["count"]

    status, _, body = _request(
        headers={"Content-Type": "text/plain"},
    )

    status_after, _, body_after = _request()
    after = _json(body_after)["count"]

    assert status_before == 200
    assert status == 415
    assert status_after == 200
    assert after == before + 1

    payload = _json(body)
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message", "requestId"}
    assert payload["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
