import numpy
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN

from ..order.type import Order


def calculate_distance(
  start: tuple[float, float],
  end: tuple[float, float],
) -> float:
  return geodesic(start, end).kilometers


def calculate_basket_center(orders: list[Order]) -> tuple[float, float]:
  if not orders:
    return 0.0, 0.0

  latitudes = [order.latitude for order in orders]
  longitudes = [order.longitude for order in orders]

  return numpy.mean(latitudes), numpy.mean(longitudes)


def calculate_basket_radius(
  center: tuple[float, float],
  orders: list[Order],
) -> float:
  if not orders:
    return 0.0

  max_distance = 0.0
  for order in orders:
    distance = calculate_distance(center, (order.latitude, order.longitude))
    max_distance = max(max_distance, distance)

  return max_distance


def cluster_orders(orders: list[Order], radius: float) -> numpy.ndarray:
  epsilon_radians = (radius / 2.0) / 6371.0

  dbscan = DBSCAN(
    eps=epsilon_radians,
    min_samples=1,
    metric="haversine",
    algorithm="ball_tree",
  )

  coordinates = [[order.latitude, order.longitude] for order in orders]
  coordinates_array = numpy.array(coordinates)
  coordinates_radians = numpy.radians(coordinates_array)

  return dbscan.fit_predict(coordinates_radians)
