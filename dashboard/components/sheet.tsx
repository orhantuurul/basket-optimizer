import { SheetHeader } from "@/components/sheet-header";
import { ScrollArea } from "@/components/ui/scroll-area";

type SheetProps = {
  children: React.ReactNode;
};

export function Sheet({ children }: SheetProps) {
  return (
    <aside className="w-[440px] border-r border-border/80 bg-sidebar flex flex-col h-full overflow-hidden">
      <div className="px-10 py-8 border-b border-border/40 bg-sidebar shrink-0">
        <SheetHeader />
      </div>
      <ScrollArea className="flex-1 min-h-0">
        <div className="px-10 py-8">{children}</div>
      </ScrollArea>
    </aside>
  );
}
