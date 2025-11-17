import { Order } from "./order";

export type Basket = {
  latitude: number;
  longitude: number;
  radius: number;
  orders: Order[];
};
