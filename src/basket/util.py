import numpy
from geopy.distance import geodesic

from ..order.type import Order


def cluster_orders(orders: list[Order], radius: float) -> list[list[Order]]:
  """
  Cluster orders into baskets ensuring:
  1. All orders in a basket are within 2*radius (diameter) of each other
  2. Each order belongs to exactly one basket
  3. Minimize the number of baskets (greedy approach)

  Args:
      orders: List of orders to cluster
      radius: Maximum radius for each basket in kilometers
              (diameter = 2 * radius)

  Returns:
      List of clusters, where each cluster is a list of orders
  """
  unassigned_orders = sorted(orders, key=lambda o: (o.latitude, o.longitude))
  clusters: list[list[Order]] = []

  while unassigned_orders:
    # Start new cluster with first unassigned order
    seed_order = unassigned_orders.pop(0)
    new_cluster = [seed_order]

    # Try to add orders that fit within diameter constraint
    i = 0
    while i < len(unassigned_orders):
      candidate = unassigned_orders[i]

      # Check if candidate is within 2*radius of ALL orders in cluster
      fits_in_cluster = all(
        calculate_distance(
          (existing.latitude, existing.longitude),
          (candidate.latitude, candidate.longitude),
        )
        <= 2 * radius
        for existing in new_cluster
      )

      if fits_in_cluster:
        new_cluster.append(unassigned_orders.pop(i))
      else:
        i += 1

    clusters.append(new_cluster)

  return clusters


def calculate_distance(
  start: tuple[float, float],
  end: tuple[float, float],
) -> float:
  """Calculate distance between two points in kilometers"""
  return geodesic(start, end).kilometers


def calculate_basket_center(orders: list[Order]) -> tuple[float, float]:
  """Calculate the geometric center of a list of orders"""
  if not orders:
    return 0.0, 0.0

  latitudes = [order.latitude for order in orders]
  longitudes = [order.longitude for order in orders]

  return numpy.mean(latitudes), numpy.mean(longitudes)
