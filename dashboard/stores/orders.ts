import { Order } from "@/types/order";
import { create } from "zustand";

interface OrdersState {
  orders: Order[];
  setOrders: (orders: Order[]) => void;
}

export const useOrders = create<OrdersState>((set) => ({
  orders: [],
  setOrders: (orders) => set({ orders }),
}));
