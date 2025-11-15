from src.basket.util import calculate_distance
from src.order.type import Order


def validate_cluster(orders: list[Order], radius: float) -> bool:
  """
  Validate that all orders in a cluster are within the diameter constraint.

  Args:
      orders: List of orders in the cluster
      radius: Maximum radius for the basket

  Returns:
      True if cluster is valid, False otherwise
  """
  if len(orders) <= 1:
    return True

  diameter = 2 * radius

  # Check all pairs of orders
  for i, order1 in enumerate(orders):
    for order2 in orders[i + 1 :]:
      distance = calculate_distance(
        (order1.latitude, order1.longitude), (order2.latitude, order2.longitude)
      )
      if distance > diameter:
        return False

  return True


def get_max_distance_in_cluster(orders: list[Order]) -> float:
  """
  Get the maximum distance between any two orders in a cluster.

  Args:
      orders: List of orders in the cluster

  Returns:
      Maximum distance in kilometers
  """
  if len(orders) <= 1:
    return 0.0

  max_dist = 0.0
  for i, order1 in enumerate(orders):
    for order2 in orders[i + 1 :]:
      distance = calculate_distance(
        (order1.latitude, order1.longitude), (order2.latitude, order2.longitude)
      )
      max_dist = max(max_dist, distance)

  return max_dist


def check_order_uniqueness(clusters: list[list[Order]]) -> bool:
  """
  Check that each order appears in exactly one cluster.

  Args:
      clusters: List of clusters

  Returns:
      True if all orders are unique across clusters
  """
  seen_orders = set()

  for cluster in clusters:
    for order in cluster:
      order_tuple = (order.latitude, order.longitude)
      if order_tuple in seen_orders:
        return False
      seen_orders.add(order_tuple)

  return True
