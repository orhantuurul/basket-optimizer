import json

from .type import Region


async def get_regions() -> list[Region]:
  """
  Loads geographic regions from coordinates.json file.

  Reads a GeoJSON FeatureCollection file and converts each feature
  into a Region object. Supports both Polygon and MultiPolygon
  geometry types.

  Args:
    None. Reads from "coordinates.json" file in the current directory.

  Returns:
    List of Region objects, each containing name, type, and coordinates
    from the GeoJSON features. Returns empty list if file contains no
    features.

  Raises:
    FileNotFoundError: If coordinates.json file does not exist.
    json.JSONDecodeError: If the file contains invalid JSON.
    KeyError: If required GeoJSON structure is missing.
  """
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
