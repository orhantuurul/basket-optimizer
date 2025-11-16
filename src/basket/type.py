from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel
from sanic_ext import openapi

from ..order.type import Order


@openapi.component(name="Basket")
class Basket(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  latitude: float
  longitude: float
  radius: float
  orders: list[Order]

  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


class Baskets(RootModel[list[Basket]]):
  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


@openapi.component(name="BasketsCreate")
class BasketsCreate(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  orders: list[Order] = Field(description="List of orders")

  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")
