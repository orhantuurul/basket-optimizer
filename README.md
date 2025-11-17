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
# Build and start all services in detached mode
docker compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8080` and the dashboard at `http://localhost:3000`.

## Algorithm

The service uses a two-phase approach:

1. **Spatial Indexing**: Builds a cKDTree for fast radius queries
2. **Set Cover Optimization**: Uses OR-Tools to find the minimum number of baskets covering all orders

## Requirements

- Python 3.13+
- uv (package manager)
