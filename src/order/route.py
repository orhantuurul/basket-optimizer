from sanic import Blueprint, Request, json
from sanic.response import JSONResponse
from sanic_ext import openapi

from . import service
from .type import OrderCreate, Orders

route = Blueprint("order", url_prefix="/orders")


@route.post("/batch")
@openapi.body({"application/json": OrderCreate.json()})
@openapi.response(201, {"application/json": Orders.json()})
async def create_orders(request: Request) -> JSONResponse:
  """Create orders"""
  body = OrderCreate.model_validate(request.json)
  orders = await service.create_orders(body)
  return json([order.model_dump() for order in orders], status=201)
