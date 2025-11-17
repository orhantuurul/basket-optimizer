import pytest
from scipy.spatial import cKDTree

from src.basket.util import (
  build_spatial_tree,
  calculate_distance,
  query_radius_tree,
)
from src.order.type import Order


def test_calculate_distance_same_point():
  """
  Tests distance calculation from a point to itself.

  Verifies that the Haversine distance calculation returns zero
  when both points are identical.
  """
  point = (40.7128, -74.0060)
  distance = calculate_distance(point, point)
  assert distance == 0.0


def test_calculate_distance_known_distance():
  """
  Tests distance calculation with known real-world coordinates.

  Verifies accuracy by calculating distance between New York City and
  Philadelphia, which should be approximately 120-140 km.
  """
  nyc = (40.7128, -74.0060)
  philly = (39.9526, -75.1652)
  distance = calculate_distance(nyc, philly)

  assert 120 <= distance <= 140


def test_calculate_distance_accuracy():
  """
  Tests distance calculation accuracy for nearby points.

  Verifies that the Haversine formula correctly calculates short
  distances (approximately 0.5 km) between nearby coordinates.
  """
  point1 = (40.7128, -74.0060)
  point2 = (40.7173, -74.0060)
  distance = calculate_distance(point1, point2)

  assert 0.4 <= distance <= 0.6


def test_build_spatial_tree_empty():
  """
  Tests building spatial tree from empty order list.

  Verifies that attempting to build a cKDTree from an empty list
  raises an appropriate ValueError.
  """
  with pytest.raises(ValueError, match="data must be of shape"):
    build_spatial_tree([])


def test_build_spatial_tree_single_order():
  """
  Tests building spatial tree from a single order.

  Verifies that a cKDTree is correctly constructed with one point
  and contains the expected number of data points.
  """
  orders = [Order(latitude=40.7128, longitude=-74.0060)]
  tree = build_spatial_tree(orders)

  assert isinstance(tree, cKDTree)
  assert tree.n == 1


def test_build_spatial_tree_multiple_orders():
  """
  Tests building spatial tree from multiple orders.

  Verifies that a cKDTree correctly indexes multiple orders and
  contains the expected number of data points.
  """
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7130, longitude=-74.0062),
    Order(latitude=40.7140, longitude=-74.0070),
  ]
  tree = build_spatial_tree(orders)

  assert isinstance(tree, cKDTree)
  assert tree.n == 3


def test_query_radius_tree_single_point():
  """
  Tests radius query with single point at center.

  Verifies that querying a tree containing only the center point
  returns that point's index within the specified radius.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  orders = [center]

  tree = build_spatial_tree(orders)
  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 1
  assert result[0] == 0


def test_query_radius_tree_within_radius():
  """
  Tests radius query for points within the search radius.

  Verifies that the function correctly identifies and returns indices
  of points that fall within the specified radius from the center.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  nearby = Order(latitude=40.7150, longitude=-74.0060)
  orders = [center, nearby]

  tree = build_spatial_tree(orders)
  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) >= 1
  assert 0 in result


def test_query_radius_tree_outside_radius():
  """
  Tests radius query for points outside the search radius.

  Verifies that points beyond the specified radius are correctly
  excluded from the results, even if they are in the tree.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  far = Order(latitude=40.7218, longitude=-74.0060)
  orders = [center, far]

  tree = build_spatial_tree(orders)
  result = query_radius_tree(tree, center, 0.5, orders)

  assert 0 in result
  assert 1 not in result


def test_query_radius_tree_boundary():
  """
  Tests radius query for points exactly at the radius boundary.

  Verifies that points at exactly 0.5 km from the center are correctly
  included in the results, testing boundary condition handling.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  from geopy.distance import geodesic

  distance = geodesic(kilometers=0.5)
  point = distance.destination((center.latitude, center.longitude), bearing=0)
  boundary = Order(latitude=point.latitude, longitude=point.longitude)

  orders = [center, boundary]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 2


def test_query_radius_tree_empty_result():
  """
  Tests radius query when no points are within radius.

  Verifies that when all points in the tree are beyond the search
  radius, the function returns an empty list.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  orders = [Order(latitude=50.0, longitude=-80.0)]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 0


def test_query_radius_tree_precision():
  """
  Tests handling of floating-point precision in radius queries.

  Verifies that points with very similar coordinates are correctly
  processed, ensuring numerical stability in distance calculations.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)
  close = Order(latitude=40.7128001, longitude=-74.0060001)
  orders = [center, close]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 2


def test_build_spatial_tree_coordinates():
  """
  Tests that spatial tree uses correct coordinate order.

  Verifies that the tree correctly indexes coordinates in the
  [latitude, longitude] format and returns accurate radius queries.
  """
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7130, longitude=-74.0062),
  ]
  tree = build_spatial_tree(orders)

  center = Order(latitude=40.7129, longitude=-74.0061)
  result = query_radius_tree(tree, center, 0.1, orders)

  assert len(result) >= 1
