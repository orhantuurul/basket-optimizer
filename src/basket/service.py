from .type import Basket, BasketsCreate
from .util import (
  calculate_basket_center,
  calculate_basket_radius,
  cluster_orders,
)


async def create_baskets(body: BasketsCreate) -> list:
  if not body.orders:
    return []

  baskets = []
  clusters = cluster_orders(body.orders, body.radius)

  for cluster in set(clusters):
    if cluster == -1:
      continue

    mask = clusters == cluster
    orders = [
      body.orders[index]
      for index, is_in_cluster in enumerate(mask)
      if is_in_cluster
    ]

    latitude, longitude = calculate_basket_center(orders)
    radius = calculate_basket_radius((latitude, longitude), orders)

    basket = Basket(
      latitude=latitude,
      longitude=longitude,
      radius=round(radius, 3),
      orders=orders,
    )
    baskets.append(basket)

  return baskets
