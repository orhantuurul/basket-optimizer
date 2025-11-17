from geopy.distance import geodesic
from scipy.spatial import cKDTree

from ..order.type import Order


def calculate_distance(
  start: tuple[float, float],
  end: tuple[float, float],
) -> float:
  """
  Calculate the great circle distance between two points on Earth
  using the Haversine formula.

  Args:
      start: First point as tuple (latitude, longitude)
      end: Second point as tuple (latitude, longitude)

  Returns:
      Distance in kilometers
  """
  distance = geodesic(start, end)
  return distance.kilometers


def build_spatial_tree(orders: list[Order]) -> cKDTree:
  """
  Build a spatial index (cKDTree) from orders for fast radius queries.

  Note: cKDTree uses Euclidean distance, which is an approximation for
  geospatial coordinates. We use it for fast filtering, then validate
  with Haversine distance for accuracy.

  Args:
    orders: List of orders with latitude/longitude

  Returns:
    cKDTree spatial index
  """
  coordinates = [[order.latitude, order.longitude] for order in orders]
  return cKDTree(coordinates)


def query_radius_tree(
  tree: cKDTree,
  center: Order,
  radius: float,
  orders: list[Order],
) -> list[int]:
  """
  Query spatial tree for points within radius, validated with Haversine.

  Uses cKDTree for fast candidate selection, then validates with
  Haversine distance for geospatial accuracy.

  Args:
    tree: cKDTree spatial index
    center: Center point (Order)
    radius_km: Radius in kilometers
    orders: List of all orders (for validation)

  Returns:
    List of indices of orders within the radius (inclusive of boundary)
  """
  radius_deg = radius / 111.0

  center_coord = [center.latitude, center.longitude]
  candidate_indices = tree.query_ball_point(center_coord, radius_deg)

  valid_indices = []
  for idx in candidate_indices:
    order = orders[idx]
    distance = calculate_distance(
      (center.latitude, center.longitude),
      (order.latitude, order.longitude),
    )
    if distance <= radius + 1e-9:
      valid_indices.append(idx)

  return valid_indices
