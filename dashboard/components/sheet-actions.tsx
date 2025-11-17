"use client";

import { fetcher, FetchError } from "@/lib/fetcher";
import { useBaskets } from "@/stores/baskets";
import { useOrders } from "@/stores/orders";
import { Region } from "@/types/region";
import { PackageSearch, Play, RotateCcw } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "./ui/button";

type SheetActionsProps = {
  selectedRegions: Region[];
};

export function SheetActions({ selectedRegions }: SheetActionsProps) {
  const { orders, setOrders } = useOrders();
  const { baskets, setBaskets } = useBaskets();
  const [creatingOrders, setCreatingOrders] = useState(false);
  const [creatingBaskets, setCreatingBaskets] = useState(false);

  const handleCreateOrders = async () => {
    try {
      setCreatingOrders(true);

      const regions = selectedRegions.map((region) => region.name);
      const orders = await fetcher
        .post("/api/orders/batch", { regions })
        .then((response) => response.json());

      setOrders(orders);
      setBaskets([]);
    } catch (error) {
      const description =
        error instanceof FetchError ? error.data?.message : String(error);
      toast.error("Failed to create orders", { description });
    } finally {
      setCreatingOrders(false);
    }
  };

  const handleCreateBaskets = async () => {
    try {
      setCreatingBaskets(true);

      const baskets = await fetcher
        .post("/api/baskets/batch", { orders: orders })
        .then((response) => response.json());

      setBaskets(baskets);
    } catch (error) {
      const description =
        error instanceof FetchError ? error.data?.message : String(error);
      toast.error("Failed to create orders", { description });
    } finally {
      setCreatingBaskets(false);
    }
  };

  const handleReset = () => {
    setOrders([]);
    setBaskets([]);
  };

  return (
    <div className="space-y-4 pt-2">
      <h2 className="text-xs font-medium text-muted-foreground tracking-wider uppercase">
        Actions
      </h2>
      <div className="space-y-3">
        <Button
          onClick={handleCreateOrders}
          disabled={selectedRegions.length === 0 || creatingOrders}
          className="w-full h-12 text-base font-medium cursor-pointer"
          size="lg"
        >
          <Play className="h-4 w-4" />
          {creatingOrders ? "Creating..." : "Create Orders"}
        </Button>
        <div className="grid grid-cols-2 gap-3">
          <Button
            onClick={handleCreateBaskets}
            disabled={orders.length === 0 || creatingBaskets}
            className="w-full h-12 cursor-pointer"
            size="lg"
            variant="secondary"
          >
            <PackageSearch className="h-4 w-4" />
            {creatingBaskets ? "Creating..." : "Baskets"}
          </Button>
          <Button
            onClick={handleReset}
            disabled={orders.length === 0 && baskets.length === 0}
            className="w-full h-12 cursor-pointer"
            size="lg"
            variant="ghost"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
        </div>
      </div>
    </div>
  );
}
