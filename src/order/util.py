import random

from shapely import MultiPolygon, Point, Polygon

from ..region.type import Region


def region_polygon(region: Region) -> Polygon | MultiPolygon:
  coordinates = region.coordinates

  if region.type == "Polygon":
    return Polygon(coordinates[0])
  else:
    polygons = [Polygon(coordinate[0]) for coordinate in coordinates]
    return MultiPolygon(polygons)


def point_in_polygon(polygon: Polygon | MultiPolygon) -> tuple[float, float]:
  minx, miny, maxx, maxy = polygon.bounds

  while True:
    x = random.uniform(minx, maxx)
    y = random.uniform(miny, maxy)

    point = Point(x, y)
    if polygon.contains(point):
      return point.x, point.y
