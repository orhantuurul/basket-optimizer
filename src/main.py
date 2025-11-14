from sanic import Blueprint, Sanic

from .basket.route import route as basket_route
from .config import Config
from .errorhandler import ErrorHandler
from .region.route import route as region_route


def create_app():
  app = Sanic("basket-optimizer", error_handler=ErrorHandler())

  with_config(app)
  with_routes(app)

  return app


def with_config(app: Sanic):
  Config(app)


def with_routes(app: Sanic):
  app.blueprint(
    Blueprint.group(
      basket_route,
      region_route,
      url_prefix="/api",
    ),
  )
