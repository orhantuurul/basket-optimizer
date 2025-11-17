"use client";

import { useBaskets } from "@/stores/baskets";
import { useOrders } from "@/stores/orders";
import { Region } from "@/types/region";
import { LatLngTuple } from "leaflet";
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet/dist/leaflet.css";
import { Circle, MapContainer, Polygon, Popup, TileLayer } from "react-leaflet";

type MapProps = {
  selectedRegions: Region[];
};

const ISTANBUL_COORDINATES: LatLngTuple = [41.0082, 28.9784];

export function Map({ selectedRegions }: MapProps) {
  const { orders } = useOrders();
  const { baskets } = useBaskets();

  return (
    <div className="flex-1 relative rounded-xl overflow-hidden shadow-lg">
      <MapContainer
        center={ISTANBUL_COORDINATES}
        zoom={10}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
        zoomControl={false}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {selectedRegions?.map((region: Region) => {
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
                pathOptions={{
                  color: "oklch(0.488 0.243 264.376)",
                  fillColor: "oklch(0.488 0.243 264.376)",
                  fillOpacity: 0.08,
                  weight: 2,
                }}
              />
            );
          });
        })}
        {baskets?.map((basket, index) => {
          return (
            <div key={`${basket.latitude}-${basket.longitude}-${index}`}>
              <Circle
                center={[basket.latitude, basket.longitude]}
                radius={basket.radius * 1000}
                pathOptions={{
                  color: "oklch(0.645 0.246 16.439)",
                  fillColor: "oklch(0.645 0.246 16.439)",
                  fillOpacity: 0.1,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="font-medium text-sm">
                    <div>Orders: {basket.orders.length}</div>
                    <div>Radius: {basket.radius * 2} km</div>
                    <div>Center:</div>
                    <div className="ml-2">
                      Latitude: {basket.latitude.toFixed(6)}
                      <br />
                      Longitude: {basket.longitude.toFixed(6)}
                    </div>
                  </div>
                </Popup>
              </Circle>
              {basket.orders.map((order, index) => (
                <Circle
                  key={`${order.latitude}-${order.longitude}-${index}`}
                  center={[order.latitude, order.longitude]}
                  radius={15}
                  pathOptions={{
                    color: "oklch(0.488 0.243 264.376)",
                    fillColor: "oklch(0.488 0.243 264.376)",
                    fillOpacity: 0.7,
                    weight: 1,
                  }}
                >
                  <Popup>
                    <div className="font-medium text-sm">
                      <div className="font-bold mb-1">Order in Basket</div>
                      <div>Latitude: {order.latitude.toFixed(6)}</div>
                      <div>Longitude: {order.longitude.toFixed(6)}</div>
                    </div>
                  </Popup>
                </Circle>
              ))}
            </div>
          );
        })}
        {baskets.length == 0 &&
          orders?.map((order, index) => (
            <Circle
              key={`${order.latitude}-${order.longitude}-${index}`}
              center={[order.latitude, order.longitude]}
              radius={20}
              pathOptions={{
                color: "oklch(0.488 0.243 264.376)",
                fillColor: "oklch(0.488 0.243 264.376)",
                fillOpacity: 0.7,
                weight: 1,
              }}
            >
              <Popup>
                <div className="font-medium text-sm">
                  <div>
                    <strong>Coordinates</strong>
                  </div>
                  <div>Latitude: {order.latitude.toFixed(6)}</div>
                  <div>Longitude: {order.longitude.toFixed(6)}</div>
                </div>
              </Popup>
            </Circle>
          ))}
      </MapContainer>
    </div>
  );
}
