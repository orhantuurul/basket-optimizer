from sanic import Blueprint, Request, json
from sanic.response import JSONResponse
from sanic_ext import openapi

from . import service
from .type import Baskets, BasketsCreate

route = Blueprint("basket", url_prefix="/baskets")


@route.post("/batch")
@openapi.body({"application/json": BasketsCreate.json()})
@openapi.response(200, {"application/json": Baskets.json()})
async def create_baskets(request: Request) -> JSONResponse:
  """Create baskets for orders"""
  body = BasketsCreate.model_validate(request.json)
  baskets = await service.create_baskets(body)
  return json([basket.model_dump() for basket in baskets], status=201)
