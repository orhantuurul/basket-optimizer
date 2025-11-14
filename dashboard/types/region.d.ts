export type Region = {
  name: string;
  type: "Polygon" | "MultiPolygon";
  coordinates: number[][][] | number[][][][];
};
