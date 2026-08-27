from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)


class APIException(Exception):
    status_code = 500
    payload = None

    def __init__(self, payload=None, status_code=None):
        self.payload = payload if payload is not None else {"error": "Internal server error"}
        if status_code is not None:
            self.status_code = status_code
        super().__init__()


class ValidationError422(APIException):
    status_code = 422

    def __init__(self, details):
        super().__init__(
            payload={
                "error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": details}
            }
        )


class ConflictError(APIException):
    def __init__(self, payload, status_code=409):
        super().__init__(payload=payload, status_code=status_code)


def api_exception_handler(exc, context):
    if isinstance(exc, APIException):
        return Response(exc.payload, status=exc.status_code)

    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)) or response.status_code == 401:
        response.data = {"error": "Unauthorized"}
        if isinstance(exc, AuthenticationFailed) and str(exc.detail) not in (
            "Given token not valid for any token type",
            "Authentication credentials were not provided.",
        ):
            response.data = {"error": str(exc.detail)}
    elif isinstance(exc, PermissionDenied) or response.status_code == 403:
        response.data = {"error": "Forbidden"}
    elif isinstance(exc, NotFound) or response.status_code == 404:
        response.data = {"error": "Not found"}

    return response
