from shapely import MultiPolygon, Point, Polygon

from src.order.util import point_in_polygon, region_polygon
from src.region.type import Region


def test_region_polygon_single():
  """
  Tests conversion of a single Polygon region to Shapely Polygon.

  Verifies that a Region object with type "Polygon" is correctly converted
  to a Shapely Polygon object with valid area.
  """
  region = Region(
    name="Test",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  result = region_polygon(region)

  assert isinstance(result, Polygon)
  assert result.area > 0


def test_region_polygon_multi():
  """
  Tests conversion of a MultiPolygon region to Shapely MultiPolygon.

  Verifies that a Region object with type "MultiPolygon" is correctly
  converted to a Shapely MultiPolygon object containing multiple polygons.
  """
  region = Region(
    name="Test",
    type="MultiPolygon",
    coordinates=[
      [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
      [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
    ],
  )

  result = region_polygon(region)

  assert isinstance(result, MultiPolygon)
  assert len(result.geoms) == 2


def test_point_in_polygon_single():
  """
  Tests generation of a random point inside a single polygon.

  Verifies that the generated point lies within or on the boundary of
  the polygon using Shapely's contains or touches methods.
  """
  polygon = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])

  x, y = point_in_polygon(polygon)

  point = Point(x, y)
  assert polygon.contains(point) or polygon.touches(point)


def test_point_in_polygon_multi():
  """
  Tests generation of a random point inside a MultiPolygon.

  Verifies that the generated point lies within or on the boundary of
  at least one of the MultiPolygon's constituent polygons.
  """
  polygons = [
    Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
    Polygon([[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]),
  ]
  multi = MultiPolygon(polygons)

  x, y = point_in_polygon(multi)

  point = Point(x, y)
  assert multi.contains(point) or multi.touches(point)


def test_point_in_polygon_deterministic_bounds():
  """
  Tests that generated points are within polygon bounding box.

  Verifies that multiple generated points all fall within the polygon's
  bounding box coordinates, ensuring the rejection sampling algorithm
  respects spatial boundaries.
  """
  polygon = Polygon([[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]])

  for _ in range(10):
    x, y = point_in_polygon(polygon)
    assert 0 <= x <= 10
    assert 0 <= y <= 10


def test_point_in_polygon_complex_shape():
  """
  Tests generation of a random point in a complex polygon shape.

  Verifies that the rejection sampling algorithm correctly handles
  non-rectangular polygons with irregular boundaries.
  """
  polygon = Polygon([[0, 0], [5, 0], [5, 2], [2, 2], [2, 5], [0, 5], [0, 0]])

  x, y = point_in_polygon(polygon)

  point = Point(x, y)
  assert polygon.contains(point) or polygon.touches(point)
