from sanic import Blueprint, Request, json
from sanic.response import JSONResponse
from sanic_ext import openapi

from . import service
from .type import Regions

route = Blueprint("region", url_prefix="/regions")


@route.get("/")
@openapi.response(200, {"application/json": Regions.json()})
async def get_regions(_: Request) -> JSONResponse:
  """Get regions"""
  regions = await service.get_regions()
  return json([region.model_dump() for region in regions])
