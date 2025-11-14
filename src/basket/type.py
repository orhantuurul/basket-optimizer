from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel
from sanic_ext import openapi


@openapi.component(name="Basket")
class Basket(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  latitude: float
  longitude: float

  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


class Baskets(RootModel[list[Basket]]):
  @classmethod
  def json(cls) -> dict[str, Any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")
