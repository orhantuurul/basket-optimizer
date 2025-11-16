import pytest

from src.basket.service import create_baskets
from src.basket.type import BasketsCreate
from src.basket.util import calculate_distance
from src.order.type import Order


@pytest.mark.asyncio
async def test_empty_orders():
  """Empty input should return empty baskets."""
  body = BasketsCreate(orders=[])
  baskets = await create_baskets(body)
  assert baskets == []


@pytest.mark.asyncio
async def test_single_order():
  """Single order should create one basket."""
  body = BasketsCreate(orders=[Order(latitude=40.7128, longitude=-74.0060)])
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 1
  assert baskets[0].radius == 0.5
  assert baskets[0].orders[0].latitude == 40.7128
  assert baskets[0].orders[0].longitude == -74.0060


@pytest.mark.asyncio
async def test_identical_coordinates():
  """Multiple orders at same location should be in one basket."""
  coords = Order(latitude=40.7128, longitude=-74.0060)
  body = BasketsCreate(orders=[coords, coords, coords])
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 3
  assert baskets[0].radius == 0.5


@pytest.mark.asyncio
async def test_dense_cluster():
  """Many orders within 0.5km should be in minimal baskets."""
  # Create cluster around NYC (40.7128, -74.0060)
  # 0.1km ≈ 0.0009 degrees
  base_lat, base_lon = 40.7128, -74.0060
  orders = [
    Order(latitude=base_lat + i * 0.0001, longitude=base_lon + i * 0.0001)
    for i in range(10)
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  # All should be in 1-2 baskets (depending on optimal solution)
  assert len(baskets) <= 2
  assert sum(len(b.orders) for b in baskets) == 10


@pytest.mark.asyncio
async def test_sparse_orders():
  """Orders far apart should require separate baskets."""
  # Orders 1km apart (beyond 0.5km radius)
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7218, longitude=-74.0060),  # ~1km north
    Order(latitude=40.7128, longitude=-73.9960),  # ~1km east
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  # Each should be in separate basket
  assert len(baskets) == 3
  assert all(len(b.orders) == 1 for b in baskets)


@pytest.mark.asyncio
async def test_boundary_condition():
  """Orders exactly at 0.5km boundary should be included."""
  # Center point
  center = Order(latitude=40.7128, longitude=-74.0060)

  # Point exactly 0.5km away (approximately 0.0045 degrees)
  # Using geopy to calculate exact offset
  from geopy.distance import geodesic

  point_05km = geodesic(kilometers=0.5).destination(
    (center.latitude, center.longitude), bearing=0
  )
  boundary_order = Order(
    latitude=point_05km.latitude, longitude=point_05km.longitude
  )

  body = BasketsCreate(orders=[center, boundary_order])
  baskets = await create_baskets(body)

  # Should be in one basket (boundary included)
  assert len(baskets) == 1
  assert len(baskets[0].orders) == 2


@pytest.mark.asyncio
async def test_all_orders_assigned():
  """Every order must be assigned to exactly one basket."""
  orders = [
    Order(latitude=40.7128 + i * 0.001, longitude=-74.0060 + i * 0.001)
    for i in range(20)
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  # Collect all assigned orders
  assigned = []
  for basket in baskets:
    assigned.extend(basket.orders)

  # All orders must be assigned
  assert len(assigned) == len(orders)
  # No duplicates
  assert len(assigned) == len(set((o.latitude, o.longitude) for o in assigned))


@pytest.mark.asyncio
async def test_radius_constraint():
  """All orders in a basket must be within 0.5km of center."""
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
  """Same input should produce same output."""
  orders = [
    Order(latitude=40.7128 + i * 0.0003, longitude=-74.0060 + i * 0.0003)
    for i in range(10)
  ]
  body = BasketsCreate(orders=orders)

  baskets1 = await create_baskets(body)
  baskets2 = await create_baskets(body)

  # Same number of baskets
  assert len(baskets1) == len(baskets2)

  # Same basket structure (sorted by center for comparison)
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
  """Algorithm should minimize number of baskets."""
  # Create 3 clusters, each with 5 orders within 0.5km
  clusters = [
    (40.7128, -74.0060),  # NYC
    (40.7228, -74.0060),  # ~1.1km north
    (40.7128, -73.9960),  # ~1.1km east
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

  # Should use 3 baskets (one per cluster)
  assert len(baskets) == 3
  assert sum(len(b.orders) for b in baskets) == 15


@pytest.mark.asyncio
async def test_precision_edge_cases():
  """Test floating-point precision handling."""
  # Very close coordinates (precision edge case)
  orders = [
    Order(latitude=40.7128, longitude=-74.0060),
    Order(latitude=40.7128000001, longitude=-74.0060000001),
    Order(latitude=40.7128000002, longitude=-74.0060000002),
  ]
  body = BasketsCreate(orders=orders)
  baskets = await create_baskets(body)

  # Should handle precision correctly
  assert len(baskets) >= 1
  assert sum(len(b.orders) for b in baskets) == 3


@pytest.mark.asyncio
async def test_mixed_density():
  """Mix of dense and sparse orders."""
  # Dense cluster
  cluster_orders = [
    Order(latitude=40.7128 + i * 0.0001, longitude=-74.0060 + i * 0.0001)
    for i in range(8)
  ]

  # Sparse orders (far away)
  sparse_orders = [
    Order(latitude=40.7228, longitude=-74.0060),  # ~1.1km north
    Order(latitude=40.7128, longitude=-73.9960),  # ~1.1km east
  ]

  body = BasketsCreate(orders=cluster_orders + sparse_orders)
  baskets = await create_baskets(body)

  # Cluster should be in 1-2 baskets, sparse in separate
  assert len(baskets) >= 2
  assert sum(len(b.orders) for b in baskets) == 10

  # Verify radius constraint
  for basket in baskets:
    center = (basket.latitude, basket.longitude)
    for order in basket.orders:
      distance = calculate_distance(center, (order.latitude, order.longitude))
      assert distance <= 0.5 + 1e-9


@pytest.mark.asyncio
async def test_radius_strictly_05km():
  """Basket radius must be exactly 0.5km."""
  body = BasketsCreate(orders=[Order(latitude=40.7128, longitude=-74.0060)])
  baskets = await create_baskets(body)

  assert all(b.radius == 0.5 for b in baskets)


@pytest.mark.asyncio
async def test_orders_just_outside_boundary():
  """Orders just beyond 0.5km should be in separate baskets."""
  center = Order(latitude=40.7128, longitude=-74.0060)

  # Point just beyond 0.5km (0.51km)
  from geopy.distance import geodesic

  point_051km = geodesic(kilometers=0.51).destination(
    (center.latitude, center.longitude), bearing=0
  )
  outside_order = Order(
    latitude=point_051km.latitude, longitude=point_051km.longitude
  )

  body = BasketsCreate(orders=[center, outside_order])
  baskets = await create_baskets(body)

  # Should be in separate baskets
  assert len(baskets) == 2
  assert all(len(b.orders) == 1 for b in baskets)
