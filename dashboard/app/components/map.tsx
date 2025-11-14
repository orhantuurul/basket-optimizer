"use client";

import { Region } from "@/types/region";
import { LatLngTuple } from "leaflet";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet/dist/leaflet.css";
import { MapContainer, Polygon, TileLayer } from "react-leaflet";
import useSWR from "swr";

type MapProps = {
  selectedRegions: string[];
};

export function Map({ selectedRegions }: MapProps) {
  const { data: regions } = useSWR<Region[]>("/api/regions");

  const filteredRegions = regions?.filter((region) =>
    selectedRegions.includes(region.name)
  );

  return (
    <div className="flex-1 relative">
      <MapContainer
        center={[41.0082, 28.9784]}
        zoom={10}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {filteredRegions?.flatMap((region: Region) => {
          const coordiantes =
            region.type === "MultiPolygon"
              ? (region.coordinates as number[][][][])
              : [region.coordinates as number[][][]];

          return coordiantes.map((coordiante, index) => {
            const positions = coordiante
              .flat()
              .map((point: number[]) => [point[1], point[0]] as LatLngTuple);

            return (
              <Polygon
                key={`${region.name}-${index}`}
                positions={positions}
                pathOptions={{ color: "oklch(0.141 0.005 285.823)", weight: 2 }}
              />
            );
          });
        })}
      </MapContainer>
    </div>
  );
}
