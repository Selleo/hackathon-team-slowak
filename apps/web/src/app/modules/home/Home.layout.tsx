import { AppSidebar } from "@/components/navigation/Sidebar.tsx";
import { AppHeader } from "@/app/modules/home/Header.tsx";
import { SidebarProvider } from "@/components/ui/sidebar.tsx";
import { Outlet } from "react-router-dom";

const HomeLayout = () => {
  return (
    <SidebarProvider>
      <AppSidebar />
      <AppHeader />
      <main className="flex-1 overflow-y-auto">{<Outlet />}</main>
    </SidebarProvider>
  );
};

export default HomeLayout;
