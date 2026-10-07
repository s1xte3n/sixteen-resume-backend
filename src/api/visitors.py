from .errors import ApiError
from src.domain.ports import VisitorCounter


def handle_visitors_request(request, counter: VisitorCounter) -> dict:
    if request.method != "GET":
        raise ApiError(405, "METHOD_NOT_ALLOWED", "Only GET is supported.")

    _validate_query(request)
    _validate_body(request)

    return {"count": counter.increment()}


def _validate_query(request) -> None:
    if request.params:
        raise ApiError(400, "BAD_REQUEST", "Query parameters are not supported.")


def _validate_body(request) -> None:
    body = request.get_body()
    if body:
        raise ApiError(400, "BAD_REQUEST", "Request body is not supported.")
