import { Basket } from "@/types/basket";
import { create } from "zustand";

interface BasketsState {
  baskets: Basket[];
  setBaskets: (baskets: Basket[]) => void;
}

export const useBaskets = create<BasketsState>((set) => ({
  baskets: [],
  setBaskets: (baskets) => set({ baskets }),
}));
