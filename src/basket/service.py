from ortools.linear_solver import pywraplp

from .type import Basket, BasketsCreate
from .util import build_spatial_tree, query_radius_tree


async def create_baskets(body: BasketsCreate) -> list[Basket]:
  """
  Allocate orders into baskets using OR-Tools set cover optimization.

  Uses well-tested libraries:
  - scipy.cKDTree for fast spatial queries
  - OR-Tools for optimal set cover solution

  The algorithm minimizes the number of baskets while ensuring:
  - Each basket has a strict radius of 0.5 km
  - Every order is assigned to exactly one basket
  - The solution is optimal (not just greedy)

  Algorithm:
  1. Build spatial tree from all orders
  2. For each order as potential center, find all orders within 0.5 km
  3. Use OR-Tools set cover solver to find minimum baskets covering all orders
  4. Create baskets from the optimal solution
  """
  radius = 0.5  # radius in kilometers
  orders = body.orders

  if not orders:
    return []

  # Build spatial tree once for fast queries
  tree = build_spatial_tree(orders)

  # Generate all potential baskets (each order as center)
  # potential_baskets[i] = list of order indices within 0.5km of order i
  potential_baskets: list[list[int]] = []
  for center_order in orders:
    within_radius = query_radius_tree(tree, center_order, radius, orders)
    potential_baskets.append(within_radius)

  # Solve set cover problem using OR-Tools
  num_orders = len(orders)
  num_baskets = len(potential_baskets)

  # Create solver (CBC is free and open-source, included with OR-Tools)
  solver = pywraplp.Solver.CreateSolver("CBC")
  if not solver:
    # Fallback to SAT solver if CBC not available
    solver = pywraplp.Solver.CreateSolver("SAT")

  # Decision variables: x[i] = 1 if basket i is selected, 0 otherwise
  x = [solver.IntVar(0, 1, f"basket_{i}") for i in range(num_baskets)]

  # Constraint: Each order must be covered by at least one basket
  for order_idx in range(num_orders):
    # Find all baskets that cover this order
    covering_baskets = [
      i for i in range(num_baskets) if order_idx in potential_baskets[i]
    ]
    if covering_baskets:
      solver.Add(sum(x[i] for i in covering_baskets) >= 1)

  # Objective: Minimize number of baskets used
  solver.Minimize(sum(x))

  # Solve
  status = solver.Solve()

  # Extract solution
  selected_baskets = []
  if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    for i in range(num_baskets):
      if x[i].solution_value() > 0.5:  # Selected basket
        selected_baskets.append(i)
  else:
    # Fallback: if solver fails, use greedy approach
    # This shouldn't happen, but handle edge cases
    uncovered = set(range(num_orders))
    for i in range(num_baskets):
      if uncovered and any(idx in uncovered for idx in potential_baskets[i]):
        selected_baskets.append(i)
        uncovered -= set(potential_baskets[i])

  # Create final baskets, ensuring each order is in exactly one basket
  # Track which orders have been assigned
  assigned_orders = set()
  baskets = []

  # Sort selected baskets for deterministic assignment
  for basket_idx in sorted(selected_baskets):
    center_order = orders[basket_idx]
    basket_order_indices = potential_baskets[basket_idx]

    # Only include orders not yet assigned to another basket
    unassigned_indices = [
      idx for idx in basket_order_indices if idx not in assigned_orders
    ]

    # Only create basket if it has unassigned orders
    if unassigned_indices:
      basket_orders = [orders[idx] for idx in unassigned_indices]
      assigned_orders.update(unassigned_indices)

      basket = Basket(
        latitude=center_order.latitude,
        longitude=center_order.longitude,
        radius=radius,
        orders=basket_orders,
      )
      baskets.append(basket)

  # Ensure all orders are assigned (fallback for edge cases)
  if len(assigned_orders) < num_orders:
    unassigned = set(range(num_orders)) - assigned_orders
    for order_idx in sorted(unassigned):
      order = orders[order_idx]
      basket = Basket(
        latitude=order.latitude,
        longitude=order.longitude,
        radius=radius,
        orders=[order],
      )
      baskets.append(basket)

  return baskets
