import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";

const AgentTypingAnimation = () => (
  <>
    <style>{`
      @keyframes dot-blink {
        0%, 60%, 100% { opacity: 0.4; }
        30% { opacity: 1; }
      }
      .typing-dot {
        opacity: 0.4; 
        animation: dot-blink 1.4s infinite;
      }
      .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
      }
      .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
      }
    `}</style>
    <span className="flex gap-1">
      <span className="typing-dot">•</span>
      <span className="typing-dot">•</span>
      <span className="typing-dot">•</span>
    </span>
  </>
);

export const DraftPage = () => {
  const { currentUser } = useCurrentUserStore();
  return (
    <>
      <h1 className="text-2xl font-bold">Example Draft Title</h1>
      <div className="flex-1 flex flex-col justify-start items-center overflow-y-scroll h-full max-h-4/6 gap-2">
        <div className="flex flex-row-reverse gap-2 self-end align-center">
          <Avatar className="size-7 mt-2">
            <AvatarFallback className="size-full">
              {currentUser?.username?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <span className="bg-primary border border-sidebar-border rounded-full px-4 py-2 text-center">
            Example user message
          </span>
        </div>

        <div className="flex gap-2 self-start align-center">
          <Avatar className="size-7 mt-2">
            <AvatarImage src="/logo.png" />
            <AvatarFallback>
              <Skeleton className="w-full h-full" />
            </AvatarFallback>
          </Avatar>
          <span className="bg-accent border border-sidebar-border rounded-full px-4 py-2 text-center flex gap-1">
            Example agent response
          </span>
        </div>

        <div className="flex gap-2 self-start align-center">
          <Avatar className="size-7 mt-2">
            <AvatarImage src="/logo.png" />
            <AvatarFallback>
              <Skeleton className="w-full h-full" />
            </AvatarFallback>
          </Avatar>
          <span className="bg-accent border border-sidebar-border rounded-full px-4 py-2 text-center flex gap-1">
            <AgentTypingAnimation />
          </span>
        </div>
      </div>

      <div className="flex flex-col w-full border-t border-sidebar-border p-4 bg-background gap-2">
        <form className="flex gap-2">
          <Input
            type="text"
            placeholder="Message AI agent..."
            className="flex-1 bg-input border border-sidebar-border rounded-full px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <Button className="bg-primary text-primary-foreground rounded-full px-4 py-2 font-medium hover:bg-secondary cursor-pointer transition-colors">
            Send
          </Button>
        </form>
        <div className="flex justify-center">
          <Button
            variant="outline"
            className="bg-foreground text-background rounded-full px-4 py-2 font-medium hover:bg-secondary cursor-pointer transition-colors"
          >
            Mark as completed
          </Button>
        </div>
      </div>
    </>
  );
};
