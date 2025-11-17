import random

from shapely import MultiPolygon, Point, Polygon

from ..region.type import Region


def region_polygon(region: Region) -> Polygon | MultiPolygon:
  """
  Converts a Region object to a Shapely Polygon or MultiPolygon.

  Transforms the region's coordinate data into a Shapely geometry object
  based on the region type. Handles both single Polygon and MultiPolygon
  geometries.

  Args:
    region: Region object containing type and coordinates data.

  Returns:
    Polygon if region type is "Polygon", MultiPolygon if region type is
    "MultiPolygon". The returned geometry can be used for spatial
    operations like point-in-polygon tests.
  """
  coordinates = region.coordinates

  if region.type == "Polygon":
    return Polygon(coordinates[0])
  else:
    polygons = [Polygon(coordinate[0]) for coordinate in coordinates]
    return MultiPolygon(polygons)


def point_in_polygon(polygon: Polygon | MultiPolygon) -> tuple[float, float]:
  """
  Generates a random point inside the given polygon.

  Uses rejection sampling: generates random points within the polygon's
  bounding box until one is found that lies inside the polygon. This
  ensures uniform distribution within the polygon boundaries.

  Args:
    polygon: Shapely Polygon or MultiPolygon object to generate a point within.

  Returns:
    Tuple of (longitude, latitude) coordinates as floats. The point is
    guaranteed to be inside the polygon (or one of its components for
    MultiPolygon).
  """
  minx, miny, maxx, maxy = polygon.bounds

  while True:
    x = random.uniform(minx, maxx)
    y = random.uniform(miny, maxy)

    point = Point(x, y)
    if polygon.contains(point):
      return point.x, point.y
