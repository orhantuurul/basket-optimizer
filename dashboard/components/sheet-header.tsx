import { Package } from "lucide-react";

export function SheetHeader() {
  return (
    <div className="flex items-start gap-5">
      <Package className="h-12 w-12 text-foreground bg-secondary rounded-md p-2" />
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold text-foreground leading-none">
          Basket Optimizer
        </h1>
        <p className="text-xs text-muted-foreground font-light">
          Basket optimization tool
        </p>
      </div>
    </div>
  );
}
