import json
import uuid

from .errors import ApiError


_ALLOWED_CONTENT_TYPE = "application/json"


def handle_visitors_request(request, counter) -> dict:
    if request.method != "GET":
        raise ApiError(405, "METHOD_NOT_ALLOWED", "Only GET is supported.")

    _validate_content_type(request)
    _validate_query(request)
    _validate_body(request)

    return {"count": counter.increment()}


def _validate_content_type(request) -> None:
    content_type = request.headers.get("Content-Type")
    if content_type and content_type.split(";", 1)[0].strip().lower() != _ALLOWED_CONTENT_TYPE:
        raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Content-Type is not supported.")


def _validate_query(request) -> None:
    if request.params:
        raise ApiError(400, "BAD_REQUEST", "Query parameters are not supported.")


def _validate_body(request) -> None:
    body = request.get_body()
    if not body:
        return

    content_type = request.headers.get("Content-Type", "")
    if content_type.split(";", 1)[0].strip().lower() == _ALLOWED_CONTENT_TYPE:
        try:
            json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError(400, "BAD_REQUEST", "Request body must contain valid JSON.")
    raise ApiError(400, "BAD_REQUEST", "Request body is not supported.")


def is_uuid_v4(value: str) -> bool:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return parsed.version == 4
