import json

from .type import Region


async def get_regions() -> list[Region]:
  with open("coordinates.json", "r") as file:
    data = json.load(file)

    regions = []
    for feature in data["features"]:
      name = feature["properties"]["name"]
      type = feature["geometry"]["type"]
      coordinates = feature["geometry"]["coordinates"]

      region = Region(name=name, type=type, coordinates=coordinates)
      regions.append(region)

    return regions
