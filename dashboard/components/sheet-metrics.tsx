"use client";

import { useBaskets } from "@/stores/baskets";
import { useOrders } from "@/stores/orders";

export function SheetMetrics() {
  const { orders } = useOrders();
  const { baskets } = useBaskets();

  return (
    <div className="space-y-4">
      <h2 className="text-xs font-medium text-muted-foreground tracking-wider uppercase">
        Metrics
      </h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <p className="text-2xl font-semibold text-foreground">
            {orders.length}
          </p>
          <p className="text-xs text-muted-foreground font-light">
            Total Orders
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-2xl font-semibold text-foreground">
            {baskets.length}
          </p>
          <p className="text-xs text-muted-foreground font-light">Baskets</p>
        </div>
      </div>
    </div>
  );
}
