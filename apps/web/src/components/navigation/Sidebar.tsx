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
  UserIcon,
  LogOut,
  AlertCircleIcon,
  BookPlus,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDrafts } from "@/app/api/queries/useDrafts.ts";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Alert, AlertDescription } from "@/components/ui/alert.tsx";
import useCreateDraft from "@/app/api/mutations/useCreateDraft.ts";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";

export const AppSidebar = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [draftTitle, setDraftTitle] = useState("");
  const { data: draftsData, isSuccess, isLoading } = useDrafts();
  const { mutateAsync: createDraft } = useCreateDraft();

  const handleOpenDialog = () => {
    setIsDialogOpen(true);
  };

  const handleCreateDraft = async () => {
    await createDraft({ draftName: draftTitle });
    setDraftTitle("");
    setIsDialogOpen(false);
  };
  const { currentUser } = useCurrentUserStore();

  return (
    <Sidebar className="border-r">
      <SidebarHeader className="border-b px-4 py-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Avatar className="size-8">
              <AvatarImage src="/logo.png" alt="Luma logo" />
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

              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <button
                    onClick={handleOpenDialog}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg transition-all hover:bg-accent w-full text-left"
                  >
                    <BookPlus className="size-4" />
                    <span>Create new Draft</span>
                  </button>
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
                      {isLoading ? (
                        <Item variant="outline">
                          <ItemContent>
                            <ItemTitle>Loading...</ItemTitle>
                            <ItemDescription>
                              It may take a while
                            </ItemDescription>
                          </ItemContent>
                        </Item>
                      ) : isSuccess ? (
                        draftsData && draftsData.length > 0 ? (
                          draftsData.map((item) => (
                            <SidebarMenuSubItem key={item.id}>
                              <SidebarMenuSubButton asChild>
                                <NavLink
                                  to={`/draft/${item.id}`}
                                  className={({ isActive }) =>
                                    `flex items-center gap-2 ${
                                      isActive ? "bg-accent" : ""
                                    }`
                                  }
                                >
                                  <span>{item.draftName}</span>
                                </NavLink>
                              </SidebarMenuSubButton>
                            </SidebarMenuSubItem>
                          ))
                        ) : (
                          <Item className="mt-2" variant="outline">
                            <ItemContent>
                              <ItemTitle>No Drafts Found</ItemTitle>
                              <ItemDescription>
                                You have no drafts available.
                              </ItemDescription>
                            </ItemContent>
                            <ItemActions>
                              <Button
                                onClick={handleOpenDialog}
                                className="cursor-pointer hover:bg-secondary"
                              >
                                Create new Draft
                              </Button>
                            </ItemActions>
                          </Item>
                        )
                      ) : (
                        <Alert variant="destructive">
                          <AlertCircleIcon />
                          <AlertDescription>
                            Unable to load drafts. Please try again later.
                          </AlertDescription>
                        </Alert>
                      )}
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
                <AvatarFallback>
                  {currentUser?.username.at(0)?.toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-semibold truncate">
                  {currentUser?.username}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {currentUser?.email}
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

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Draft</DialogTitle>
            <DialogDescription>
              Enter a title for your new draft.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="Draft title..."
              value={draftTitle}
              onChange={(e) => setDraftTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && draftTitle.trim()) {
                  handleCreateDraft();
                }
              }}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDialogOpen(false);
                setDraftTitle("");
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateDraft} disabled={!draftTitle.trim()}>
              Create Draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Sidebar>
  );
};
