import { AppSidebar } from "@/components/navigation/Sidebar.tsx";
import { AppHeader } from "@/app/modules/Home/Header.tsx";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar.tsx";
import type { ReactElement } from "react";

const HomeLayout = ({ children }: { children: ReactElement }) => {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <AppHeader />
        <main className="w-full overflow-y-auto p-4 lg:p-8">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
};

export default HomeLayout;
