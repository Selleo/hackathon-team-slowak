import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarMenu,
  SidebarFooter,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar.tsx";
import {
  NotebookPen,
  NotebookTabs,
  FileText,
  Calendar,
  Tag,
} from "lucide-react";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button.tsx";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible.tsx";
import { Link, NavLink } from "react-router-dom";

const handleLogout = () => {
  console.log("User logged out");
};

const drafts = [
  {
    title: "Marketing Campaign 2024",
    url: "/drafts/1",
    icon: NotebookPen,
    submenu: [
      { title: "Introduction", url: "/drafts/1/intro", icon: FileText },
      { title: "Schedule", url: "/drafts/1/schedule", icon: Calendar },
      { title: "Tags", url: "/drafts/1/tags", icon: Tag },
    ],
  },
  {
    title: "Product Roadmap Q1",
    url: "/drafts/2",
    icon: NotebookPen,
    submenu: [
      { title: "Overview", url: "/drafts/2/overview", icon: FileText },
      { title: "Timeline", url: "/drafts/2/timeline", icon: Calendar },
      { title: "Categories", url: "/drafts/2/categories", icon: Tag },
    ],
  },
  {
    title: "Team Meeting Notes",
    url: "/drafts/3",
    icon: NotebookPen,
    submenu: [
      { title: "Agenda", url: "/drafts/3/agenda", icon: FileText },
      { title: "Action Items", url: "/drafts/3/actions", icon: Calendar },
    ],
  },
];

export const AppSidebar = () => {
  return (
    <Sidebar>
      <SidebarHeader className="border-b px-6 py-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Luma
        </h1>
      </SidebarHeader>

      <SidebarContent className="flex flex-col">
        <SidebarGroup className="">
          <SidebarGroupLabel className="mb-2 py-2 text-xs items-center flex font-semibold uppercase tracking-wider text-muted-foreground">
            <NotebookTabs className="mr-2 h-4 w-4 inline" />
            Your Drafts
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {drafts.map((draft) => (
                <Collapsible key={draft.title} className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton className="data-[state=open]:bg-primary/10 data-[state=open]:text-primary">
                        <draft.icon className="h-4 w-4" />
                        <span className="font-medium">{draft.title}</span>
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        {draft.submenu.map((item) => (
                          <SidebarMenuSubItem key={item.title}>
                            <SidebarMenuSubButton asChild>
                              <NavLink
                                to={item.url}
                                className="hover:text-primary"
                              >
                                <item.icon className="h-3 w-3" />
                                <span>{item.title}</span>
                              </NavLink>
                            </SidebarMenuSubButton>
                          </SidebarMenuSubItem>
                        ))}
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t p-4">
        <Button onClick={handleLogout} variant="destructive" className="w-full">
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
};
