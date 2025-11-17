import json
from unittest.mock import mock_open, patch

import pytest

from src.region.service import get_regions
from src.region.type import Region


@pytest.mark.asyncio
async def test_get_regions_single_polygon():
  """
  Tests loading regions from GeoJSON with single Polygon geometry.

  Verifies that a GeoJSON FeatureCollection with a single Polygon feature
  is correctly parsed and converted to a Region object.
  """
  mock_data = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {"name": "TestRegion"},
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
      }
    ],
  }

  with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
    regions = await get_regions()

  assert len(regions) == 1
  assert regions[0].name == "TestRegion"
  assert regions[0].type == "Polygon"


@pytest.mark.asyncio
async def test_get_regions_multi_polygon():
  """
  Tests loading regions from GeoJSON with MultiPolygon geometry.

  Verifies that a GeoJSON FeatureCollection with a MultiPolygon feature
  is correctly parsed and converted to a Region object.
  """
  mock_data = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {"name": "MultiRegion"},
        "geometry": {
          "type": "MultiPolygon",
          "coordinates": [
            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
          ],
        },
      }
    ],
  }

  with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
    regions = await get_regions()

  assert len(regions) == 1
  assert regions[0].name == "MultiRegion"
  assert regions[0].type == "MultiPolygon"


@pytest.mark.asyncio
async def test_get_regions_multiple_regions():
  """
  Tests loading multiple regions from GeoJSON FeatureCollection.

  Verifies that a GeoJSON file containing multiple features is correctly
  parsed, with each feature converted to a separate Region object.
  """
  mock_data = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {"name": "Region1"},
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
      },
      {
        "type": "Feature",
        "properties": {"name": "Region2"},
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
        },
      },
    ],
  }

  with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
    regions = await get_regions()

  assert len(regions) == 2
  assert {r.name for r in regions} == {"Region1", "Region2"}


@pytest.mark.asyncio
async def test_get_regions_empty_features():
  """
  Tests loading empty GeoJSON FeatureCollection.

  Verifies that a GeoJSON file with no features returns an empty
  list of regions without errors.
  """
  mock_data = {"type": "FeatureCollection", "features": []}

  with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
    regions = await get_regions()

  assert len(regions) == 0


@pytest.mark.asyncio
async def test_region_model_validation():
  """
  Tests that Region model validates and stores data correctly.

  Verifies that a Region object can be instantiated with valid data
  and that all attributes are correctly stored and accessible.
  """
  region = Region(
    name="Test",
    type="Polygon",
    coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
  )

  assert region.name == "Test"
  assert region.type == "Polygon"
  assert len(region.coordinates) == 1
