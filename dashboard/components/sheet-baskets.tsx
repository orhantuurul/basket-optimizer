"use client";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Basket } from "@/types/basket";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

type SheetBasketsProps = {
  baskets: Basket[];
};

export function SheetBaskets({ baskets }: SheetBasketsProps) {
  const [openBaskets, setOpenBaskets] = useState<Set<number>>(new Set());

  const handleOpenChange = (index: number, open: boolean) => {
    setOpenBaskets((prev) => {
      const next = new Set(prev);
      if (open) {
        next.add(index);
        return next;
      }

      next.delete(index);
      return next;
    });
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xs font-medium text-muted-foreground tracking-wider uppercase">
        Baskets
      </h2>
      <div className="space-y-3">
        {baskets.map((basket, index) => {
          const opened = openBaskets.has(index);
          const ChevronIcon = opened ? ChevronDown : ChevronRight;

          return (
            <Collapsible
              key={`basket-${index}`}
              open={opened}
              onOpenChange={() => handleOpenChange(index, !opened)}
              className="border rounded-xl overflow-hidden"
            >
              <CollapsibleTrigger className="w-full px-4 py-3 text-left">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ChevronIcon className="h-3.5 w-3.5 text-muted-foreground/60" />
                    <span className="text-xs font-medium text-foreground">
                      Basket {index + 1}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground font-light">
                    {basket.orders.length}{" "}
                    {basket.orders.length === 1 ? "order" : "orders"}
                  </span>
                </div>
                <div className="mt-2 text-[10px] text-muted-foreground/60 font-light">
                  Radius: {(basket.radius * 2).toFixed(1)} km
                </div>
              </CollapsibleTrigger>
              <CollapsibleContent className="px-4 py-3 space-y-2">
                {basket.orders.map((order, orderIndex) => (
                  <div
                    key={`order-${index}-${orderIndex}`}
                    className="flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <div className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                      <span className="text-muted-foreground font-light">
                        Order {orderIndex + 1}
                      </span>
                    </div>
                    <span className="text-muted-foreground/60 font-mono text-[10px]">
                      {order.latitude.toFixed(4)}, {order.longitude.toFixed(4)}
                    </span>
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </div>
    </div>
  );
}
