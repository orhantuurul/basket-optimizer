from .type import Basket, BasketsCreate
from .util import calculate_basket_center, cluster_orders


async def create_baskets(body: BasketsCreate) -> list:
  if not body.orders:
    return []

  # Cluster orders using diameter constraint
  clusters = cluster_orders(body.orders, body.radius)

  baskets = []
  for cluster in clusters:
    # Calculate the geometric center of the cluster
    latitude, longitude = calculate_basket_center(cluster)

    basket = Basket(
      latitude=latitude,
      longitude=longitude,
      radius=body.radius,
      orders=cluster,
    )
    baskets.append(basket)

  return baskets
