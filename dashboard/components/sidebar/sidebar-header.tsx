import { Package } from "lucide-react";

export function SidebarHeader() {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Package className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-foreground">
            Basket Optimizer
          </h1>
          <p className="text-sm text-muted-foreground">
            Basket optimizing experience
          </p>
        </div>
      </div>
    </div>
  );
}
