import pytest

from src.basket.service import create_baskets
from src.basket.type import BasketsCreate
from src.basket.util import calculate_distance
from src.order.type import Order


@pytest.mark.asyncio
async def test_empty_orders():
  """
  Tests basket creation with empty order list.

  Verifies that when no orders are provided, the function returns
  an empty list of baskets.
  """
  body = BasketsCreate(orders=[])
  baskets = await create_baskets(body)
  assert baskets == []


@pytest.mark.asyncio
async def test_single_order():
  """
  Tests basket creation with a single order.

  Verifies that a single order creates exactly one basket with the
  order's coordinates as the basket center and radius of 0.5 km.
  """
  body = BasketsCreate(orders=[Order(latitude=40.7128, longitude=-74.0060)])
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 1
  assert baskets[0].radius == 0.5
  assert baskets[0].orders[0].latitude == 40.7128
  assert baskets[0].orders[0].longitude == -74.0060


@pytest.mark.asyncio
async def test_identical_coordinates():
  """
  Tests basket creation with multiple orders at identical coordinates.

  Verifies that orders with the same location are grouped into a
  single basket with radius 0.5 km.
  """
  coords = Order(latitude=40.7128, longitude=-74.0060)
  body = BasketsCreate(orders=[coords, coords, coords])
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 3
  assert baskets[0].radius == 0.5


@pytest.mark.asyncio
async def test_dense_cluster():
  """
  Tests basket creation with dense order clusters.

  Verifies that many orders within 0.5 km of each other are grouped
  into minimal number of baskets, demonstrating optimization efficiency.
  """
  base_lat, base_lon = 40.7128, -74.0060
  orders = [
    Order(latitude=base_lat + i * 0.0001, longitude=base_lon + i * 0.0001)
    for i in range(10)
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  assert len(baskets) <= 2
  assert sum(len(b.orders) for b in baskets) == 10


@pytest.mark.asyncio
async def test_sparse_orders():
  """
  Tests basket creation with orders far apart.

  Verifies that orders separated by more than 0.5 km are placed
  in separate baskets, each containing a single order.
  """
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7218, longitude=-74.0060),
    Order(latitude=40.7128, longitude=-73.9960),
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  assert len(baskets) == 3
  assert all(len(b.orders) == 1 for b in baskets)


@pytest.mark.asyncio
async def test_boundary_condition():
  """
  Tests basket creation with orders at the 0.5 km boundary.

  Verifies that orders exactly at the 0.5 km radius boundary are
  correctly included in the same basket, testing edge case handling.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)

  from geopy.distance import geodesic

  point_05km = geodesic(kilometers=0.5).destination(
    (center.latitude, center.longitude), bearing=0
  )
  boundary_order = Order(
    latitude=point_05km.latitude, longitude=point_05km.longitude
  )

  body = BasketsCreate(orders=[center, boundary_order])
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 2


@pytest.mark.asyncio
async def test_all_orders_assigned():
  """
  Tests that all orders are assigned to exactly one basket.

  Verifies complete coverage: every order appears in exactly one basket
  with no duplicates or missing assignments.
  """
  orders = [
    Order(latitude=40.7128 + i * 0.001, longitude=-74.0060 + i * 0.001)
    for i in range(20)
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  assigned = []
  for basket in baskets:
    assigned.extend(basket.orders)

  assert len(assigned) == len(orders)
  assert len(assigned) == len(set((o.latitude, o.longitude) for o in assigned))


@pytest.mark.asyncio
async def test_radius_constraint():
  """
  Tests that all orders in a basket are within 0.5 km of center.

  Verifies the strict radius constraint by checking that every order
  in each basket is within 0.5 km (with small floating-point tolerance)
  of the basket's center coordinates.
  """
  orders = [
    Order(latitude=40.7128 + i * 0.0005, longitude=-74.0060 + i * 0.0005)
    for i in range(15)
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  for basket in baskets:
    center = (basket.latitude, basket.longitude)
    for order in basket.orders:
      distance = calculate_distance(center, (order.latitude, order.longitude))
      assert distance <= 0.5 + 1e-9, f"Order {distance:.6f}km from center"


@pytest.mark.asyncio
async def test_deterministic_results():
  """
  Tests that identical inputs produce identical outputs.

  Verifies deterministic behavior by running the algorithm twice with
  the same input and comparing the number and structure of baskets.
  """
  orders = [
    Order(latitude=40.7128 + i * 0.0003, longitude=-74.0060 + i * 0.0003)
    for i in range(10)
  ]
  body = BasketsCreate(orders=orders)

  baskets1 = await create_baskets(body)
  baskets2 = await create_baskets(body)

  assert len(baskets1) == len(baskets2)

  baskets1_sorted = sorted(
    baskets1, key=lambda b: (b.latitude, b.longitude, len(b.orders))
  )
  baskets2_sorted = sorted(
    baskets2, key=lambda b: (b.latitude, b.longitude, len(b.orders))
  )

  assert len(baskets1_sorted) == len(baskets2_sorted)
  for b1, b2 in zip(baskets1_sorted, baskets2_sorted):
    assert len(b1.orders) == len(b2.orders)


@pytest.mark.asyncio
async def test_minimize_baskets():
  """
  Tests that the algorithm minimizes the number of baskets.

  Verifies optimization by checking that orders in distinct clusters
  are grouped efficiently, minimizing total basket count while
  maintaining the 0.5 km radius constraint.
  """
  clusters = [
    (40.7128, -74.0060),
    (40.7228, -74.0060),
    (40.7128, -73.9960),
  ]

  orders = []
  for base_lat, base_lon in clusters:
    for i in range(5):
      orders.append(
        Order(
          latitude=base_lat + i * 0.0001,
          longitude=base_lon + i * 0.0001,
        )
      )

  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  assert len(baskets) == 3
  assert sum(len(b.orders) for b in baskets) == 15


@pytest.mark.asyncio
async def test_precision_edge_cases():
  """
  Tests handling of floating-point precision edge cases.

  Verifies that orders with very similar but not identical coordinates
  are correctly processed, ensuring numerical stability in distance
  calculations.
  """
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7128000001, longitude=-74.0060000001),
    Order(latitude=40.7128000002, longitude=-74.0060000002),
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  assert len(baskets) >= 1
  assert sum(len(b.orders) for b in baskets) == 3


@pytest.mark.asyncio
async def test_mixed_density():
  """
  Tests basket creation with mixed order density.

  Verifies that the algorithm correctly handles a combination of
  dense clusters and sparse orders, creating appropriate baskets
  for each scenario while maintaining radius constraints.
  """
  cluster_orders = [
    Order(latitude=40.7128 + i * 0.0001, longitude=-74.0060 + i * 0.0001)
    for i in range(8)
  ]

  sparse_orders = [
    Order(latitude=40.7228, longitude=-74.0060),
    Order(latitude=40.7128, longitude=-73.9960),
  ]

  body = BasketsCreate(orders=cluster_orders + sparse_orders)
  baskets = await create_baskets(body)

  assert len(baskets) >= 2
  assert sum(len(b.orders) for b in baskets) == 10

  for basket in baskets:
    center = (basket.latitude, basket.longitude)
    for order in basket.orders:
      distance = calculate_distance(center, (order.latitude, order.longitude))
      assert distance <= 0.5 + 1e-9


@pytest.mark.asyncio
async def test_radius_strictly_05km():
  """
  Tests that basket radius is exactly 0.5 km.

  Verifies that all created baskets have a radius value of exactly
  0.5 km, ensuring consistency in the basket configuration.
  """
  body = BasketsCreate(orders=[Order(latitude=40.7128, longitude=-74.0060)])
  baskets = await create_baskets(body)

  assert all(b.radius == 0.5 for b in baskets)


@pytest.mark.asyncio
async def test_orders_just_outside_boundary():
  """
  Tests basket creation with orders just beyond 0.5 km boundary.

  Verifies that orders slightly beyond the 0.5 km radius are correctly
  placed in separate baskets, ensuring strict radius enforcement.
  """
  center = Order(latitude=40.7128, longitude=-74.0060)

  from geopy.distance import geodesic

  point_051km = geodesic(kilometers=0.51).destination(
    (center.latitude, center.longitude), bearing=0
  )
  outside_order = Order(
    latitude=point_051km.latitude, longitude=point_051km.longitude
  )

  body = BasketsCreate(orders=[center, outside_order])
  baskets = await create_baskets(body)

  assert len(baskets) == 2
  assert all(len(b.orders) == 1 for b in baskets)
