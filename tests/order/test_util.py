from shapely import MultiPolygon, Point, Polygon

from src.order.util import point_in_polygon, region_polygon
from src.region.type import Region


def test_region_polygon_single():
  """Test converting single Polygon region."""
  region = Region(
    name="Test",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  result = region_polygon(region)

  assert isinstance(result, Polygon)
  assert result.area > 0


def test_region_polygon_multi():
  """Test converting MultiPolygon region."""
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
  """Test generating point inside single polygon."""
  polygon = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])

  x, y = point_in_polygon(polygon)

  point = Point(x, y)
  assert polygon.contains(point) or polygon.touches(point)


def test_point_in_polygon_multi():
  """Test generating point inside MultiPolygon."""
  polygons = [
    Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
    Polygon([[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]),
  ]
  multi = MultiPolygon(polygons)

  x, y = point_in_polygon(multi)

  point = Point(x, y)
  assert multi.contains(point) or multi.touches(point)


def test_point_in_polygon_deterministic_bounds():
  """Test that generated points are within polygon bounds."""
  polygon = Polygon([[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]])

  for _ in range(10):
    x, y = point_in_polygon(polygon)
    assert 0 <= x <= 10
    assert 0 <= y <= 10


def test_point_in_polygon_complex_shape():
  """Test generating point in complex polygon shape."""
  # L-shaped polygon
  polygon = Polygon([[0, 0], [5, 0], [5, 2], [2, 2], [2, 5], [0, 5], [0, 0]])

  x, y = point_in_polygon(polygon)

  point = Point(x, y)
  assert polygon.contains(point) or polygon.touches(point)
