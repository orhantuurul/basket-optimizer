import sys

from sanic import Sanic
from sanic_cors.extension import CORS
from sanic_ext import Extend


class Config:
  runned_dev_mode = "--dev" in sys.argv
  runned_debug_mode = "--debug" in sys.argv

  DEBUG = True if runned_dev_mode or runned_debug_mode else False
  HEALTH = True if runned_dev_mode or runned_debug_mode else False
  HEALTH_ENDPOINT = True if runned_dev_mode or runned_debug_mode else False

  FALLBACK_ERROR_FORMAT = "json"
  OAS_URL_PREFIX = "/api/docs"

  def __init__(self, app: Sanic):
    app.update_config(Config)

    Extend(
      app,
      extensions=[CORS],
      config={
        "CORS": False,
        "CORS_OPTIONS": {
          "resources": r"/*",
          "origins": "*",
          "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
          "allow_headers": [
            "Content-Type",
            "X-Instance-Id",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "X-CSRF-Token",
            "X-API-Key",
          ],
          "expose_headers": [
            "Content-Type",
            "X-Instance-Id",
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
          ],
          "supports_credentials": True,
          "automatic_options": True,
          "max_age": 3600,
        },
      },
    )

    app.ext.openapi.describe(
      title="Basket Optimizer API",
      version="0.0.1",
      description="API for simulate optimizing the basket experience",
    )
