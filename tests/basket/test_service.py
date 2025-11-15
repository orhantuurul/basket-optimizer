import pytest

from src.basket.service import create_baskets
from src.basket.type import BasketsCreate
from src.order.type import Order

from .util import check_order_uniqueness, validate_cluster


@pytest.mark.asyncio
async def test_empty_orders():
  """Empty orders should return empty baskets"""
  body = BasketsCreate(orders=[], radius=1.0)
  baskets = await create_baskets(body)

  assert baskets == []


@pytest.mark.asyncio
async def test_single_order():
  """Single order should create one basket"""
  orders = [Order(latitude=41.0, longitude=29.0)]
  body = BasketsCreate(orders=orders, radius=1.0)
  baskets = await create_baskets(body)

  assert len(baskets) == 1
  assert len(baskets[0].orders) == 1
  assert baskets[0].radius == 1.0


@pytest.mark.asyncio
async def test_basket_attributes():
  """Baskets should have correct attributes"""
  orders = [
    Order(latitude=41.0, longitude=29.0),
    Order(latitude=41.001, longitude=29.001),
  ]
  body = BasketsCreate(orders=orders, radius=1.5)
  baskets = await create_baskets(body)

  assert len(baskets) > 0
  for basket in baskets:
    assert basket.radius == 1.5
    assert basket.latitude is not None
    assert basket.longitude is not None
    assert len(basket.orders) > 0


@pytest.mark.asyncio
async def test_diameter_constraint():
  """All baskets must respect diameter constraint"""
  orders = [
    Order(latitude=41.0 + i * 0.005, longitude=29.0 + i * 0.005)
    for i in range(30)
  ]
  body = BasketsCreate(orders=orders, radius=1.0)
  baskets = await create_baskets(body)

  for basket in baskets:
    assert validate_cluster(basket.orders, basket.radius), (
      "Basket violates diameter constraint"
    )


@pytest.mark.asyncio
async def test_order_uniqueness():
  """Each order should appear in exactly one basket"""
  orders = [
    Order(latitude=41.0 + i * 0.003, longitude=29.0 + i * 0.003)
    for i in range(50)
  ]
  body = BasketsCreate(orders=orders, radius=1.0)
  baskets = await create_baskets(body)

  # Extract clusters from baskets
  clusters = [basket.orders for basket in baskets]

  assert check_order_uniqueness(clusters), "Orders appear in multiple baskets"

  # All orders should be assigned
  total = sum(len(basket.orders) for basket in baskets)
  assert total == len(orders)


@pytest.mark.asyncio
async def test_basket_center_calculation():
  """Basket center should be within reasonable bounds"""
  orders = [
    Order(latitude=41.0, longitude=29.0),
    Order(latitude=41.002, longitude=29.002),
  ]
  body = BasketsCreate(orders=orders, radius=1.0)
  baskets = await create_baskets(body)

  basket = baskets[0]

  # Center should be between min and max coordinates
  lats = [o.latitude for o in orders]
  lons = [o.longitude for o in orders]

  assert min(lats) <= basket.latitude <= max(lats)
  assert min(lons) <= basket.longitude <= max(lons)


@pytest.mark.asyncio
@pytest.mark.parametrize("radius", [1.0, 2.0, 3.0])
async def test_different_radii(radius):
  """Test with different radius values"""
  orders = [
    Order(latitude=41.1 + i * 0.003, longitude=29.0 + i * 0.003)
    for i in range(25)
  ]
  body = BasketsCreate(orders=orders, radius=radius)
  baskets = await create_baskets(body)

  assert len(baskets) > 0

  for basket in baskets:
    assert basket.radius == radius
    assert validate_cluster(basket.orders, radius)
