import { useState } from "react";
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
  SidebarGroupContent,
} from "@/components/ui/sidebar.tsx";
import {
  Home,
  BookOpen,
  Settings,
  Bell,
  Search,
  ChevronDown,
  FileText,
  Calendar,
  Tag,
  UserIcon,
  LogOut,
} from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import {
  Avatar,
  AvatarImage,
  AvatarFallback,
} from "@/components/ui/avatar.tsx";
import { Input } from "@/components/ui/input";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible.tsx";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

const drafts = [
  { title: "Introduction", url: "/drafts/1/intro", icon: FileText },
  { title: "Schedule", url: "/drafts/1/schedule", icon: Calendar },
  { title: "Tags", url: "/drafts/1/tags", icon: Tag },
];

export const AppSidebar = () => {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <Sidebar className="border-r">
      <SidebarHeader className="border-b px-4 py-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Avatar className="size-8">
              <AvatarImage src="logo.png" alt="Luma logo" />
            </Avatar>
            <h1 className="text-lg font-bold">Luma</h1>
          </div>
          <button className="p-1.5 hover:bg-accent rounded-md transition-colors">
            <Bell className="size-4" />
          </button>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
          <Input
            placeholder="Search courses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-9"
          />
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 py-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink
                    to="/"
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-accent"
                      }`
                    }
                  >
                    <Home className="size-4" />
                    <span>Dashboard</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <Collapsible className="group/collapsible">
                <SidebarMenuItem>
                  <CollapsibleTrigger asChild>
                    <SidebarMenuButton className="px-3 flex gap-3 flex-row data-[state=open]:bg-accent data-[state=open]:text-accent-foreground">
                      <BookOpen className="size-4" />
                      <span>My Drafts</span>
                      <ChevronDown className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
                    </SidebarMenuButton>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <SidebarMenuSub>
                      {drafts.map((item) => (
                        <SidebarMenuSubItem key={item.title}>
                          <SidebarMenuSubButton asChild>
                            <NavLink
                              to={item.url}
                              className={({ isActive }) =>
                                `flex items-center gap-2 ${
                                  isActive ? "bg-accent" : ""
                                }`
                              }
                            >
                              <item.icon className="size-3.5" />
                              <span>{item.title}</span>
                            </NavLink>
                          </SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      ))}
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </SidebarMenuItem>
              </Collapsible>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t p-2 w-full">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-3 w-full flex-1 px-3 py-2 rounded-lg hover:bg-accent transition-colors">
              <Avatar className="size-9">
                <AvatarImage src="avatar.png" />
                <AvatarFallback>JA</AvatarFallback>
              </Avatar>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-semibold truncate">John Appleseed</p>
                <p className="text-xs text-muted-foreground truncate">
                  John@appleseed.com
                </p>
              </div>
              <Settings className="size-4 text-muted-foreground" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-60 flex flex-col gap-1">
            <DropdownMenuItem className="p-2">
              <UserIcon className="size-4" />
              Profile Settings
            </DropdownMenuItem>
            <Link to="/logout">
              <DropdownMenuItem className="text-destructive p-2">
                <LogOut className="size-4" />
                Logout
              </DropdownMenuItem>
            </Link>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  );
};
