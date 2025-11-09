import { AppSidebar } from "@/components/navigation/Sidebar.tsx";
import { AppHeader } from "@/app/modules/Home/Header.tsx";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar.tsx";
import type { ReactElement } from "react";

const HomeLayout = ({ children }: { children: ReactElement }) => {
  return (
    <SidebarProvider className="max-h-dvh">
      <AppSidebar />
      <SidebarInset>
        <AppHeader />
        <main className="flex flex-1 flex-col w-full overflow-y-auto p-4 lg:p-8 gap-2 lg:gap-4">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
};

export default HomeLayout;
