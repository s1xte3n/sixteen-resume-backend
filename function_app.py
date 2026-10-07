import json
import logging
import uuid
from typing import Any

import azure.functions as func

from src.api.errors import ApiError
from src.api.visitors import handle_visitors_request
from src.domain.errors import (
    VisitorCounterDependencyError,
    VisitorCounterTimeoutError,
)
from src.infrastructure.factory import build_visitor_counter


logger = logging.getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
counter = build_visitor_counter()


@app.route(
    route="visitors",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
def visitors(req: func.HttpRequest) -> func.HttpResponse:
    request_id = str(uuid.uuid4())

    try:
        request_id = _validated_request_id(req)
        result = handle_visitors_request(req, counter)
        return _json_response(
            status_code=200,
            body=result,
            request_id=request_id,
        )
    except ApiError as exc:
        logger.warning(
            "Visitor API request rejected request_id=%s code=%s status_code=%s",
            request_id,
            exc.code,
            exc.status_code,
        )
        return _json_response(
            status_code=exc.status_code,
            body=exc.to_body(request_id),
            request_id=request_id,
        )
    except VisitorCounterTimeoutError:
        logger.warning(
            "Visitor counter dependency timed out request_id=%s",
            request_id,
        )
        return _json_response(
            status_code=504,
            body={
                "error": {
                    "code": "DEPENDENCY_TIMEOUT",
                    "message": "The visitor counter dependency timed out.",
                    "requestId": request_id,
                }
            },
            request_id=request_id,
        )
    except VisitorCounterDependencyError:
        logger.error(
            "Visitor counter dependency unavailable request_id=%s",
            request_id,
        )
        return _json_response(
            status_code=503,
            body={
                "error": {
                    "code": "DEPENDENCY_UNAVAILABLE",
                    "message": "The visitor counter dependency is unavailable.",
                    "requestId": request_id,
                }
            },
            request_id=request_id,
        )
    except Exception:
        logger.exception(
            "Unexpected visitor API failure request_id=%s",
            request_id,
        )
        return _json_response(
            status_code=500,
            body={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "requestId": request_id,
                }
            },
            request_id=request_id,
        )


def _validated_request_id(req: func.HttpRequest) -> str:
    supplied = req.headers.get("X-Request-ID")
    if not supplied:
        return str(uuid.uuid4())

    try:
        parsed = uuid.UUID(supplied)
    except ValueError as exc:
        raise ApiError(400, "BAD_REQUEST", "X-Request-ID must be a UUID v4.") from exc

    if parsed.version != 4:
        raise ApiError(400, "BAD_REQUEST", "X-Request-ID must be a UUID v4.")

    return str(parsed)


def _json_response(
    status_code: int,
    body: dict[str, Any],
    request_id: str,
) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(body),
        status_code=status_code,
        mimetype="application/json",
        headers={"X-Request-ID": request_id},
    )
