"use client";

import { Sidebar } from "@/components/sidebar/sidebar";
import { Button } from "@/components/ui/button";
import { MultiSelect } from "@/components/ui/multi-select";
import { fetcher } from "@/lib/utils";
import { Basket } from "@/types/basket";
import { Region } from "@/types/region";
import { Play, RotateCcw } from "lucide-react";
import dynamic from "next/dynamic";
import { useState } from "react";
import useSWR from "swr";

const Map = dynamic(() => import("./components/map").then((mod) => mod.Map), {
  loading: () => <div className="flex-1 bg-background"></div>,
  ssr: false,
});

export default function Home() {
  const { data: regions } = useSWR<Region[]>("/api/regions");
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [baskets, setBaskets] = useState<Basket[]>([]);

  const handleCreateBaskets = async () => {
    await fetcher.post("/api/baskets", { regions: selectedRegions });
  };

  const handleReset = () => {
    setSelectedRegions([]);
  };

  return (
    <main className="flex h-screen w-full overflow-hidden bg-background">
      <Map selectedRegions={selectedRegions} />
      <Sidebar>
        <div className="p-6 space-y-6">
          <MultiSelect
            values={selectedRegions}
            options={
              regions?.map((region) => ({
                label: region.name,
                value: region.name,
              })) ?? []
            }
            onValuesChange={(values) => setSelectedRegions(values)}
          />
          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleCreateBaskets}
              disabled={selectedRegions.length == 0}
              className="cursor-pointer flex-1"
              size="lg"
            >
              <Play className="h-4 w-4 mr-2" />
              Create Baskets
            </Button>
            <Button
              onClick={handleReset}
              className="cursor-pointer"
              size="lg"
              variant="ghost"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Sidebar>
    </main>
  );
}
