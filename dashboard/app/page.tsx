"use client";

import { Sheet } from "@/components/sheet";
import { SheetActions } from "@/components/sheet-actions";
import { SheetBaskets as Baskets } from "@/components/sheet-baskets";
import { SheetMetrics as Metrics } from "@/components/sheet-metrics";
import { MultiSelect } from "@/components/ui/multi-select";
import { useBaskets } from "@/stores/baskets";
import { useOrders } from "@/stores/orders";
import { Region } from "@/types/region";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import useSWR from "swr";

const Map = dynamic(() => import("@/components/map").then((mod) => mod.Map), {
  loading: () => <div className="flex-1 bg-background"></div>,
  ssr: false,
});

export default function Home() {
  const { data: regions } = useSWR<Region[]>("/api/regions");
  const { orders } = useOrders();
  const { baskets } = useBaskets();
  const [selectedRegions, setSelectedRegions] = useState<Region[]>([]);

  const sortedRegions = useMemo(() => {
    const comparer = new Intl.Collator("tr-TR", { sensitivity: "base" });
    return regions?.sort((a, b) => comparer.compare(a.name, b.name));
  }, [regions]);

  const handleRegionsSelect = (values: string[]) => {
    const filtered = regions?.filter((region) => values.includes(region.name));
    setSelectedRegions(filtered ?? []);
  };

  return (
    <main className="flex h-screen w-full overflow-hidden bg-background">
      <div className="flex-1">
        <Map selectedRegions={selectedRegions} />
      </div>
      <Sheet>
        <div className="space-y-10">
          <div className="space-y-4">
            <h2 className="text-sm font-medium text-muted-foreground tracking-wider uppercase">
              Regions
            </h2>
            <MultiSelect
              values={selectedRegions.map((region) => region.name)}
              options={
                sortedRegions?.map((region) => ({
                  label: region.name,
                  value: region.name,
                })) ?? []
              }
              onValuesChange={handleRegionsSelect}
            />
          </div>
          <SheetActions selectedRegions={selectedRegions} />
          {(orders.length > 0 || baskets.length > 0) && <Metrics />}
          {baskets.length > 0 && <Baskets baskets={baskets} />}
        </div>
      </Sheet>
    </main>
  );
}
