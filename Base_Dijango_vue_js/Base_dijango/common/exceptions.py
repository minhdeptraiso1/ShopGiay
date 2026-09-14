import logging
from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _code_from_data(data: Any, default: str) -> str:
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value and hasattr(value[0], "code"):
                return str(value[0].code)
            if hasattr(value, "code"):
                return str(value.code)
    if isinstance(data, list) and data and hasattr(data[0], "code"):
        return str(data[0].code)
    return default


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", "-")

    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return Response(
            {
                "code": "server_error",
                "message": "Đã xảy ra lỗi hệ thống.",
                "details": {},
                "request_id": request_id,
            },
            status=500,
        )

    details = response.data
    message = "Yêu cầu không hợp lệ."
    if isinstance(details, dict) and "detail" in details:
        message = str(details["detail"])
    elif response.status_code == 401:
        message = "Thông tin xác thực không hợp lệ hoặc đã hết hạn."
    elif response.status_code == 403:
        message = "Bạn không có quyền thực hiện thao tác này."

    response.data = {
        "code": _code_from_data(details, getattr(exc, "default_code", "api_error")),
        "message": message,
        "details": details,
        "request_id": request_id,
    }
    return response
