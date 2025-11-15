import random

from sanic import exceptions
from shapely import MultiPolygon, unary_union

from ..region import service as region_service
from .type import Order, OrderCreate
from .util import point_in_polygon, region_polygon


async def create_orders(body: OrderCreate) -> list[Order]:
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

  combined_polygon = unary_union(polygons)

  orders = []
  for _ in range(body.count):
    if isinstance(combined_polygon, MultiPolygon):
      polygons = list(combined_polygon.geoms)
      areas = [p.area for p in polygons]
      total_area = sum(areas)
      weights = [area / total_area for area in areas]
      selected_polygon = random.choices(polygons, weights=weights)[0]
    else:
      selected_polygon = combined_polygon

    longitude, latitude = point_in_polygon(selected_polygon)
    order = Order(longitude=longitude, latitude=latitude)
    orders.append(order)

  return orders
