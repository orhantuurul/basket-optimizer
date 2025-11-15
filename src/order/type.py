from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel
from sanic_ext import openapi


@openapi.component(name="Order")
class Order(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  latitude: float
  longitude: float

  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


class Orders(RootModel[list[Order]]):
  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


@openapi.component(name="OrdersCreate")
class OrderCreate(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  regions: list[str] = Field(description="List of region names")
  count: int = Field(default=1_000, ge=1, le=10_000)

  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")
