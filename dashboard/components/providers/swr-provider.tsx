"use client";

import { fetcher } from "@/lib/fetcher";
import { SWRConfig } from "swr";

export function SwrProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        refreshInterval: 3000,
        fetcher: (resource, init) =>
          fetcher.get(resource, init).then((res) => res.json()),
      }}
    >
      {children}
    </SWRConfig>
  );
}
