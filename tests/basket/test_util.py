import pytest
from scipy.spatial import cKDTree

from src.basket.util import (
  build_spatial_tree,
  calculate_distance,
  query_radius_tree,
)
from src.order.type import Order


def test_calculate_distance_same_point():
  """Distance from point to itself should be zero."""
  point = (40.7128, -74.0060)
  distance = calculate_distance(point, point)
  assert distance == 0.0


def test_calculate_distance_known_distance():
  """Test distance calculation with known values."""
  nyc = (40.7128, -74.0060)
  philly = (39.9526, -75.1652)
  distance = calculate_distance(nyc, philly)

  assert 120 <= distance <= 140


def test_calculate_distance_accuracy():
  """Test distance calculation accuracy."""
  point1 = (40.7128, -74.0060)
  point2 = (40.7173, -74.0060)
  distance = calculate_distance(point1, point2)

  assert 0.4 <= distance <= 0.6


def test_build_spatial_tree_empty():
  """Building tree from empty list should raise error."""
  with pytest.raises(ValueError, match="data must be of shape"):
    build_spatial_tree([])


def test_build_spatial_tree_single_order():
  """Building tree from single order."""
  orders = [Order(latitude=40.7128, longitude=-74.0060)]
  tree = build_spatial_tree(orders)

  assert isinstance(tree, cKDTree)
  assert tree.n == 1


def test_build_spatial_tree_multiple_orders():
  """Building tree from multiple orders."""
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7130, longitude=-74.0062),
    Order(latitude=40.7140, longitude=-74.0070),
  ]
  tree = build_spatial_tree(orders)

  assert isinstance(tree, cKDTree)
  assert tree.n == 3


def test_query_radius_tree_single_point():
  """Query tree with single point at center."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  orders = [center]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 1
  assert result[0] == 0


def test_query_radius_tree_within_radius():
  """Query tree for points within radius."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  nearby = Order(latitude=40.7150, longitude=-74.0060)
  orders = [center, nearby]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) >= 1
  assert 0 in result


def test_query_radius_tree_outside_radius():
  """Query tree for points outside radius."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  far = Order(latitude=40.7218, longitude=-74.0060)
  orders = [center, far]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert 0 in result
  assert 1 not in result


def test_query_radius_tree_boundary():
  """Query tree for points exactly at boundary."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  from geopy.distance import geodesic

  boundary_point = geodesic(kilometers=0.5).destination(
    (center.latitude, center.longitude), bearing=0
  )
  boundary = Order(
    latitude=boundary_point.latitude, longitude=boundary_point.longitude
  )
  orders = [center, boundary]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 2


def test_query_radius_tree_empty_result():
  """Query tree with no points in radius."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  orders = [Order(latitude=50.0, longitude=-80.0)]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 0


def test_query_radius_tree_precision():
  """Test that floating-point precision is handled correctly."""
  center = Order(latitude=40.7128, longitude=-74.0060)
  close = Order(latitude=40.7128001, longitude=-74.0060001)
  orders = [center, close]
  tree = build_spatial_tree(orders)

  result = query_radius_tree(tree, center, 0.5, orders)

  assert len(result) == 2


def test_build_spatial_tree_coordinates():
  """Test that tree uses correct coordinate order."""
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7130, longitude=-74.0062),
  ]
  tree = build_spatial_tree(orders)

  center = Order(latitude=40.7129, longitude=-74.0061)
  result = query_radius_tree(tree, center, 0.1, orders)

  assert len(result) >= 1
