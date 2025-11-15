from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, RootModel
from sanic_ext import openapi


@openapi.component(name="Region")
class Region(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  name: str
  type: Literal["Polygon", "MultiPolygon"]
  coordinates: Union[
    list[list[list[float]]],
    list[list[list[list[float]]]],
  ]

  @classmethod
  def json(cls) -> dict[str, any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")


class Regions(RootModel[list[Region]]):
  @classmethod
  def json(cls) -> dict[str, any]:
    return cls.model_json_schema(ref_template="#/components/schemas/{model}")
