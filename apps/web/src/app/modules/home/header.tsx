// import { AvatarImage } from "@/components/ui/avatar.tsx";

import { SidebarTrigger } from "@/components/ui/sidebar.tsx";

export const AppHeader = () => {
  return (
    <>
      <header>
        <h1>Luma</h1>
        <SidebarTrigger />
      </header>
    </>
  );
};
