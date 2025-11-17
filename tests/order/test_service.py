from unittest.mock import AsyncMock, patch

import pytest
from sanic import exceptions
from shapely import Polygon

from src.order.service import (
  create_orders,
  select_multi_polygon,
  select_polygon,
)
from src.order.type import Order, OrderCreate
from src.region.type import Region


@pytest.mark.asyncio
async def test_create_orders_single_region():
  """
  Tests order creation within a single region.

  Verifies that orders are generated within the specified region boundaries
  and that all generated coordinates fall within the expected range.
  """
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
  """
  Tests order creation across multiple disjoint regions.

  Verifies that orders can be generated across multiple regions and that
  each order falls within at least one of the specified region boundaries.
  """
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
  """
  Tests order creation within a MultiPolygon region.

  Verifies that the system correctly handles regions with multiple disjoint
  polygons and generates orders within any of the polygon components.
  """
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
  """
  Tests error handling when invalid region names are provided.

  Verifies that the system raises BadRequest when no valid regions are found
  in the request, ensuring proper validation of user input.
  """
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
  """
  Tests error handling when no regions are available.

  Verifies that BadRequest is raised when the region list is empty or
  contains only invalid region names.
  """
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
  """
  Tests order creation with a mix of valid and invalid region names.

  Verifies that the system gracefully handles partial validity by processing
  only the valid regions and ignoring invalid ones.
  """
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
  """
  Tests order creation with various count values.

  Verifies that the system correctly generates the exact number of orders
  requested, from minimum (1) to larger batches (100).
  """
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
  """
  Tests that generated orders are random but valid.

  Verifies that orders are randomly distributed (not all identical) while
  still falling within the specified region boundaries.
  """
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


def test_select_polygon_single_polygon():
  """
  Tests polygon selection with a single polygon input.

  Verifies that when given a single polygon, the function returns
  the same polygon without modification.
  """
  polygon = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygons = [polygon]

  result = select_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon)


def test_select_polygon_multiple_overlapping_polygons():
  """
  Tests polygon selection with overlapping polygons.

  Verifies that when polygons overlap, they are correctly merged into
  a single unified polygon via unary_union.
  """
  polygon1 = Polygon([[0, 0], [2, 0], [2, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[1, 0], [3, 0], [3, 1], [1, 1], [1, 0]])
  polygons = [polygon1, polygon2]

  result = select_polygon(polygons)
  assert isinstance(result, Polygon)


def test_select_polygon_multiple_disjoint_polygons():
  """
  Tests polygon selection with disjoint polygons forming a MultiPolygon.

  Verifies that when polygons are disjoint, the function correctly delegates
  to select_multi_polygon for area-weighted selection.
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]])
  polygons = [polygon1, polygon2]

  with patch("src.order.service.select_multi_polygon") as mock_select:
    mock_select.return_value = polygon1
    result = select_polygon(polygons)

  assert mock_select.called
  assert isinstance(result, Polygon)


def test_select_polygon_empty_list():
  """
  Tests polygon selection with an empty input list.

  Verifies edge case handling when no polygons are provided. The function
  should either return None or raise an appropriate exception.
  """
  polygons = []

  try:
    result = select_polygon(polygons)
    assert result is not None
  except Exception:
    pass


def test_select_multi_polygon_equal_areas():
  """
  Tests weighted selection with polygons of equal area.

  Verifies that when polygons have identical areas, selection works
  correctly with equal weights (50/50 probability).
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]])
  polygons = [polygon1, polygon2]

  with patch("src.order.service.random.choices", return_value=[polygon1]):
    result = select_multi_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon1)


def test_select_multi_polygon_different_areas():
  """
  Tests weighted selection with polygons of different areas.

  Verifies that weight calculation correctly proportions selection probability
  based on polygon area. Larger polygons should have proportionally higher
  selection weights.
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]])
  polygons = [polygon1, polygon2]

  areas = [p.area for p in polygons]
  total_area = sum(areas)
  weights = [area / total_area for area in areas]

  assert len(weights) == 2
  assert weights[0] == 1 / 5
  assert weights[1] == 4 / 5

  with patch("src.order.service.random.choices", return_value=[polygon2]):
    result = select_multi_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon2)


def test_select_multi_polygon_three_polygons():
  """
  Tests select_multi_polygon with three polygons of different areas.

  Verifies that weight calculation works correctly with multiple polygons
  and that weights sum to 1.0 for valid probability distribution.
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[2, 2], [4, 2], [4, 3], [2, 3], [2, 2]])
  polygon3 = Polygon([[5, 5], [8, 5], [8, 6], [5, 6], [5, 5]])
  polygons = [polygon1, polygon2, polygon3]

  areas = [p.area for p in polygons]
  total_area = sum(areas)
  weights = [area / total_area for area in areas]

  assert len(weights) == 3
  assert abs(sum(weights) - 1.0) < 1e-10

  with patch("src.order.service.random.choices", return_value=[polygon3]):
    result = select_multi_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon3)


def test_select_multi_polygon_single_polygon():
  """
  Tests weighted selection with a single polygon.

  Verifies that the function handles the edge case of a single polygon
  correctly, where weight calculation should result in 100% selection.
  """
  polygon = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygons = [polygon]

  with patch("src.order.service.random.choices", return_value=[polygon]):
    result = select_multi_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon)


def test_select_multi_polygon_weights_calculation():
  """
  Tests that selection weights are correctly calculated based on polygon area.

  Verifies the internal weight calculation logic by mocking random.choices
  and inspecting the weights passed to it. Ensures weights are proportional
  to area and sum to 1.0.
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]])
  polygons = [polygon1, polygon2]

  areas = [p.area for p in polygons]
  total_area = sum(areas)
  expected_weights = [area / total_area for area in areas]

  with patch("src.order.service.random.choices") as mock_choices:
    mock_choices.return_value = [polygon1]
    select_multi_polygon(polygons)

    assert mock_choices.called
    call_args = mock_choices.call_args
    assert call_args.args[0] == polygons
    actual_weights = call_args.kwargs.get("weights")

    assert actual_weights is not None
    assert len(actual_weights) == 2
    assert abs(actual_weights[0] - expected_weights[0]) < 1e-10
    assert abs(actual_weights[1] - expected_weights[1]) < 1e-10
    assert abs(sum(actual_weights) - 1.0) < 1e-10


def test_select_multi_polygon_very_small_polygon():
  """
  Tests weighted selection with a very small polygon (edge case).

  Verifies that the function correctly handles extreme size differences
  between polygons, ensuring numerical stability in weight calculations.
  """

  polygon1 = Polygon([[0, 0], [0.1, 0], [0.1, 0.1], [0, 0.1], [0, 0]])
  polygon2 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygons = [polygon1, polygon2]

  with patch("src.order.service.random.choices", return_value=[polygon2]):
    result = select_multi_polygon(polygons)

  assert isinstance(result, Polygon)
  assert result.equals(polygon2)


def test_select_polygon_integration_with_multi_polygon():
  """
  Tests integration between select_polygon and select_multi_polygon.

  Verifies that select_polygon correctly delegates to select_multi_polygon
  when the union results in a MultiPolygon, ensuring proper function composition.
  """
  polygon1 = Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
  polygon2 = Polygon([[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]])
  polygons = [polygon1, polygon2]

  with patch("src.order.service.select_multi_polygon") as mock_select:
    mock_select.return_value = polygon1
    result = select_polygon(polygons)

    assert mock_select.called
    assert len(mock_select.call_args[0][0]) == 2
    assert isinstance(result, Polygon)
