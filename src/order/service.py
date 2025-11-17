import random

from sanic import exceptions
from shapely import MultiPolygon, Polygon, unary_union

from ..region import service as region_service
from .type import Order, OrderCreate
from .util import point_in_polygon, region_polygon


async def create_orders(body: OrderCreate) -> list[Order]:
  """
  Creates random orders within the specified geographic regions.

  Generates the requested number of orders by randomly placing points
  within the union of all specified regions. For MultiPolygon regions,
  selection is weighted by area to ensure uniform distribution.

  Args:
    body: OrderCreate request containing list of region names and
      count of orders to generate.

  Returns:
    List of Order objects, each with random latitude and longitude
    coordinates within the specified regions.

  Raises:
    BadRequest: If no valid regions are found in the request or if
      all specified region names are invalid.
  """
  regions = await region_service.get_regions()
  regions_by_names = {region.name: region for region in regions}

  target_regions = []
  for region in body.regions:
    if region in regions_by_names:
      target_regions.append(regions_by_names[region])

  if not target_regions:
    raise exceptions.BadRequest("No valid regions selected")

  polygons = []
  for region in target_regions:
    polygon = region_polygon(region)
    polygons.append(polygon)

  orders = []
  for _ in range(body.count):
    polygon = select_polygon(polygons)
    longitude, latitude = point_in_polygon(polygon)
    order = Order(longitude=longitude, latitude=latitude)
    orders.append(order)

  return orders


def select_polygon(polygons: list[Polygon | MultiPolygon]) -> Polygon:
  """
  Selects a polygon from a list, handling both single and multi-polygon cases.

  Computes the union of all input polygons. If the result is a MultiPolygon,
  delegates to select_multi_polygon for area-weighted selection. Otherwise
  returns the single Polygon directly.

  Args:
    polygons: List of Polygon or MultiPolygon objects to select from.

  Returns:
    A single Polygon object. If input polygons form a MultiPolygon after
    union, returns one of its constituent polygons selected by area weight.
    Otherwise returns the union Polygon directly.
  """
  polygon_union = unary_union(polygons)
  if isinstance(polygon_union, MultiPolygon):
    polygons = list(polygon_union.geoms)
    return select_multi_polygon(polygons)
  return polygon_union


def select_multi_polygon(polygons: list[Polygon | MultiPolygon]) -> Polygon:
  """
  Selects a polygon from a list using area-weighted random selection.

  Calculates the area of each polygon and uses these areas as weights
  for random selection. Larger polygons have proportionally higher
  probability of being selected, ensuring uniform point distribution
  across the combined area.

  Args:
    polygons: List of Polygon or MultiPolygon objects to select from.
      Each polygon's area is used as a selection weight.

  Returns:
    A single Polygon object randomly selected from the input list,
    with selection probability proportional to each polygon's area.
  """
  areas = [polygon.area for polygon in polygons]
  total_area = sum(areas)
  weights = [area / total_area for area in areas]
  return random.choices(polygons, weights=weights)[0]
