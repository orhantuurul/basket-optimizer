import { ScrollArea } from "@/components/ui/scroll-area";
import { SidebarHeader } from "./sidebar-header";

type SidebarProps = {
  children: React.ReactNode;
};

export function Sidebar({ children }: SidebarProps) {
  return (
    <aside className="w-[400px] border-r border-border bg-sidebar flex flex-col">
      <div className="p-6 border-b border-border">
        <SidebarHeader />
      </div>
      <ScrollArea>{children}</ScrollArea>
    </aside>
  );
}
