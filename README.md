# basket-optimizer

[![codecov](https://codecov.io/gh/orhantuurul/basket-optimizer/branch/main/graph/badge.svg)](https://codecov.io/gh/orhantuurul/basket-optimizer)

Geospatial basket allocation service that optimally groups orders into delivery baskets using set cover optimization.

## Features

- **Optimal Allocation**: Uses OR-Tools to minimize the number of baskets
- **Geospatial Accuracy**: Haversine distance calculations with spatial indexing
- **Strict Constraints**: Each basket has exactly 0.5km radius
- **High Performance**: O(n log n) complexity with scipy.cKDTree
- **Well Tested**: Comprehensive test suite covering all edge cases

## Quick Start

```bash
# Install dependencies
uv sync

# Run the service
uv run sanic src.main:create_app --workers=4

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

## Algorithm

The service uses a two-phase approach:

1. **Spatial Indexing**: Builds a cKDTree for fast radius queries
2. **Set Cover Optimization**: Uses OR-Tools to find the minimum number of baskets covering all orders

## Requirements

- Python 3.13+
- uv (package manager)
