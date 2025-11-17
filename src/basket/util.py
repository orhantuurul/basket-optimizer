from geopy.distance import geodesic
from scipy.spatial import cKDTree

from ..order.type import Order


def calculate_distance(
  start: tuple[float, float],
  end: tuple[float, float],
) -> float:
  """
  Calculates the great circle distance between two points on Earth.

  Uses the Haversine formula to compute the shortest distance between
  two points on the surface of a sphere (Earth), accounting for the
  planet's curvature.

  Args:
    start: First point as (latitude, longitude) tuple in degrees.
    end: Second point as (latitude, longitude) tuple in degrees.

  Returns:
    Distance between the two points in kilometers. Returns 0.0 if
    both points are identical.
  """
  distance = geodesic(start, end)
  return distance.kilometers


def build_spatial_tree(orders: list[Order]) -> cKDTree:
  """
  Builds a spatial index (cKDTree) from orders for fast radius queries.

  Creates a compressed k-d tree data structure for efficient spatial
  queries. The tree uses Euclidean distance as an approximation for
  geospatial coordinates, which is then validated with Haversine distance
  for accuracy in query_radius_tree.

  Args:
    orders: List of Order objects, each with latitude and longitude
      attributes.

  Returns:
    cKDTree spatial index containing coordinates from all orders.
    The tree can be queried for points within a given radius efficiently.

  Note:
    cKDTree uses Euclidean distance which is an approximation for
    geospatial coordinates. Results are validated with Haversine
    distance in query_radius_tree for accuracy.
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
  Queries spatial tree for points within radius, validated with Haversine.

  Uses cKDTree for fast candidate selection using Euclidean distance
  approximation, then validates each candidate with Haversine distance
  for geospatial accuracy. This two-stage approach provides both speed
  and accuracy.

  Args:
    tree: cKDTree spatial index built from orders.
    center: Center point as an Order object with latitude and longitude.
    radius: Search radius in kilometers.
    orders: List of all Order objects used to build the tree, needed
      for Haversine validation.

  Returns:
    List of integer indices corresponding to orders within the specified
    radius (inclusive of boundary). Indices refer to positions in the
    orders list.
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
