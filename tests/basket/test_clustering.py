import pytest

from src.basket.util import cluster_orders
from src.order.type import Order

from .util import (
  check_order_uniqueness,
  get_max_distance_in_cluster,
  validate_cluster,
)


def test_empty_orders():
  """Empty list should return empty clusters"""
  clusters = cluster_orders([], radius=1.0)
  assert clusters == []


def test_single_order():
  """Single order should create one cluster"""
  orders = [Order(latitude=41.0, longitude=29.0)]
  clusters = cluster_orders(orders, radius=1.0)

  assert len(clusters) == 1
  assert len(clusters[0]) == 1
  assert clusters[0][0] == orders[0]


def test_diameter_constraint():
  """All orders in each cluster must be within diameter (2*radius)"""
  orders = [
    Order(latitude=41.0, longitude=29.0),
    Order(latitude=41.005, longitude=29.005),  # ~0.7km away
    Order(latitude=41.01, longitude=29.01),  # ~1.4km from first
    Order(latitude=41.02, longitude=29.02),  # ~2.8km from first
  ]

  radius = 1.0
  clusters = cluster_orders(orders, radius)

  # Check each cluster respects diameter constraint
  for cluster in clusters:
    assert validate_cluster(cluster, radius), (
      f"Cluster violates diameter constraint: {get_max_distance_in_cluster(cluster)}km > {2 * radius}km"
    )


def test_order_uniqueness():
  """Each order should appear in exactly one cluster"""
  orders = [
    Order(latitude=41.0 + i * 0.001, longitude=29.0 + i * 0.001)
    for i in range(20)
  ]

  clusters = cluster_orders(orders, radius=1.0)

  # Check uniqueness
  assert check_order_uniqueness(clusters), "Orders appear in multiple clusters"

  # Check all orders are assigned
  total_orders = sum(len(cluster) for cluster in clusters)
  assert total_orders == len(orders), "Not all orders were assigned"


def test_close_orders_same_cluster():
  """Orders very close to each other should be in same cluster"""
  orders = [
    Order(latitude=41.0, longitude=29.0),
    Order(latitude=41.001, longitude=29.001),  # ~0.15km away
    Order(latitude=41.002, longitude=29.002),  # ~0.3km from first
  ]

  clusters = cluster_orders(orders, radius=1.0)

  # All orders should be in same cluster (all within 1km diameter)
  assert len(clusters) == 1
  assert len(clusters[0]) == 3


def test_far_orders_different_clusters():
  """Orders far apart should be in different clusters"""
  orders = [
    Order(latitude=41.0, longitude=29.0),
    Order(latitude=41.1, longitude=29.1),  # ~15km away
  ]

  clusters = cluster_orders(orders, radius=1.0)

  # Should create 2 separate clusters
  assert len(clusters) == 2
  assert len(clusters[0]) == 1
  assert len(clusters[1]) == 1


def test_max_distance_within_diameter():
  """Maximum distance in any cluster should not exceed diameter"""
  orders = [
    Order(latitude=41.0 + i * 0.002, longitude=29.0 + i * 0.002)
    for i in range(50)
  ]

  radius = 1.0
  diameter = 2 * radius
  clusters = cluster_orders(orders, radius)

  for cluster in clusters:
    max_dist = get_max_distance_in_cluster(cluster)
    assert max_dist <= diameter, (
      f"Cluster exceeds diameter: {max_dist:.3f}km > {diameter}km"
    )


def test_realistic_scenario():
  """Test with realistic order distribution"""
  # Simulate orders in Istanbul Maslak area
  orders = [
    Order(latitude=41.108 + i * 0.001, longitude=29.015 + j * 0.001)
    for i in range(10)
    for j in range(10)
  ]  # 100 orders in a grid

  radius = 1.0
  clusters = cluster_orders(orders, radius)

  # Verify constraints
  assert len(clusters) > 0, "Should create at least one cluster"
  assert check_order_uniqueness(clusters), "Orders must be unique"

  for cluster in clusters:
    assert validate_cluster(cluster, radius), (
      "Cluster violates diameter constraint"
    )
    assert len(cluster) > 0, "Clusters should not be empty"


@pytest.mark.parametrize("radius", [1.0, 2.0, 3.0, 10.0])
def test_different_radii(radius):
  """Test clustering with different radius values"""
  orders = [
    Order(latitude=41.0 + i * 0.005, longitude=29.0 + i * 0.005)
    for i in range(20)
  ]

  clusters = cluster_orders(orders, radius)

  # Basic validations
  assert len(clusters) > 0
  assert check_order_uniqueness(clusters)

  for cluster in clusters:
    assert validate_cluster(cluster, radius)
