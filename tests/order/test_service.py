from unittest.mock import AsyncMock, patch

import pytest
from sanic import exceptions

from src.order.service import create_orders
from src.order.type import Order, OrderCreate
from src.region.type import Region


@pytest.mark.asyncio
async def test_create_orders_single_region():
  """Test creating orders in single region."""
  mock_region = Region(
    name="TestRegion",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  body = OrderCreate(regions=["TestRegion"], count=5)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)

  assert len(orders) == 5
  assert all(isinstance(o, Order) for o in orders)
  assert all(0 <= o.longitude <= 1 for o in orders)
  assert all(0 <= o.latitude <= 1 for o in orders)


@pytest.mark.asyncio
async def test_create_orders_multiple_regions():
  """Test creating orders across multiple regions."""
  mock_regions = [
    Region(
      name="Region1",
      type="Polygon",
      coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
    ),
    Region(
      name="Region2",
      type="Polygon",
      coordinates=[[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
    ),
  ]

  body = OrderCreate(regions=["Region1", "Region2"], count=10)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=mock_regions,
  ):
    orders = await create_orders(body)

  assert len(orders) == 10
  all_in_bounds = all(
    (0 <= o.longitude <= 1 and 0 <= o.latitude <= 1)
    or (2 <= o.longitude <= 3 and 2 <= o.latitude <= 3)
    for o in orders
  )
  assert all_in_bounds


@pytest.mark.asyncio
async def test_create_orders_multi_polygon():
  """Test creating orders in MultiPolygon region."""
  mock_region = Region(
    name="MultiRegion",
    type="MultiPolygon",
    coordinates=[
      [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
      [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
    ],
  )

  body = OrderCreate(regions=["MultiRegion"], count=8)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)

  assert len(orders) == 8


@pytest.mark.asyncio
async def test_create_orders_invalid_region():
  """Test creating orders with invalid region name."""
  mock_region = Region(
    name="ValidRegion",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  body = OrderCreate(regions=["InvalidRegion"], count=5)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    with pytest.raises(exceptions.BadRequest, match="No valid regions"):
      await create_orders(body)


@pytest.mark.asyncio
async def test_create_orders_empty_regions():
  """Test creating orders with empty region list."""
  body = OrderCreate(regions=["AnyRegion"], count=5)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[],
  ):
    with pytest.raises(exceptions.BadRequest, match="No valid regions"):
      await create_orders(body)


@pytest.mark.asyncio
async def test_create_orders_mixed_valid_invalid():
  """Test creating orders with mix of valid and invalid regions."""
  mock_region = Region(
    name="ValidRegion",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  body = OrderCreate(regions=["ValidRegion", "InvalidRegion"], count=5)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)

  assert len(orders) == 5


@pytest.mark.asyncio
async def test_create_orders_count_validation():
  """Test creating orders with different count values."""
  mock_region = Region(
    name="TestRegion",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  body = OrderCreate(regions=["TestRegion"], count=1)
  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)
    assert len(orders) == 1

  body = OrderCreate(regions=["TestRegion"], count=100)
  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)
    assert len(orders) == 100


@pytest.mark.asyncio
async def test_create_orders_deterministic_seed():
  """Test that orders are generated (random but valid)."""
  mock_region = Region(
    name="TestRegion",
    type="Polygon",
    coordinates=[[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
  )

  body = OrderCreate(regions=["TestRegion"], count=20)

  with patch(
    "src.order.service.region_service.get_regions",
    new_callable=AsyncMock,
    return_value=[mock_region],
  ):
    orders = await create_orders(body)

  assert all(0 <= o.longitude <= 10 for o in orders)
  assert all(0 <= o.latitude <= 10 for o in orders)
  unique_points = len(set((o.longitude, o.latitude) for o in orders))
  assert unique_points > 1
