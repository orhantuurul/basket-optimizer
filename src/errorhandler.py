from typing import Any, Dict, Tuple

from pydantic import ValidationError
from sanic import json
from sanic.handlers import ErrorHandler


class ErrorHandler(ErrorHandler):
  def default(self, request, exception):
    error_handlers = {ValidationError: handle_validation_error}

    for exception_type, handler in error_handlers.items():
      if isinstance(exception, exception_type):
        response_data, status_code = handler(exception)
        return json(response_data, status=status_code)

    return super().default(request, exception)


def handle_validation_error(
  exception: ValidationError,
) -> Tuple[Dict[str, Any], int]:
  errors = []

  for error in exception.errors():
    errors.append(
      {
        "field": error["loc"][-1],
        "message": error["msg"],
        "type": error["type"],
      }
    )

  return {
    "status": "error",
    "message": "Validation error",
    "errors": errors,
  }, 422
