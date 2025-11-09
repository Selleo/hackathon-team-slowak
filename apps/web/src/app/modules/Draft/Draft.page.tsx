import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { cn } from "@/lib/utils.ts";
import { ButtonGroup } from "@/components/ui/button-group.tsx";
import { useNavigate, useParams } from "react-router-dom";
import { useCurrentDraftMessages } from "@/app/api/queries/useDraftMessages.ts";
import { useChat } from "@ai-sdk/react";
import { useEffect, useRef, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog.tsx";
import { Textarea } from "@/components/ui/textarea.tsx";
import { useCourseSchema } from "@/app/api/queries/useCourseSchema.ts";
import { queryClient } from "@/app/api/queryClient.ts";
import useExportLms from "@/app/api/mutations/useExportLms.ts";
import { useDraft } from "@/app/api/queries/useDraft.ts";

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

const ChatMessage = ({
  isAI,
  message,
}: {
  isAI: boolean;
  message: string | React.ReactNode;
}) => {
  const { currentUser } = useCurrentUserStore();

  return (
    <div
      className={cn(
        "flex gap-2 items-start max-w-1/2",
        isAI ? "self-start" : "self-end flex-row-reverse",
      )}
    >
      <Avatar className="size-7 mt-2">
        {isAI ? (
          <>
            <AvatarImage src="/logo.png" />
            <AvatarFallback>
              <Skeleton className="w-full h-full" />
            </AvatarFallback>
          </>
        ) : (
          <AvatarFallback className="size-full">
            {currentUser?.username?.charAt(0).toUpperCase()}
          </AvatarFallback>
        )}
      </Avatar>
      <span
        className={cn(
          "border border-sidebar-border rounded-xl px-4 py-2 text-start",
          isAI ? "bg-accent" : "bg-primary",
        )}
      >
        {message}
      </span>
    </div>
  );
};

interface Props {
  showGeneratedCourseDialog: boolean;
  setShowGeneratedCourseDialog: (value: boolean) => void;
  draftId: string;
}

const SchemaDialog = ({
  showGeneratedCourseDialog,
  setShowGeneratedCourseDialog,
  draftId,
}: Props) => {
  const { data } = useCourseSchema(draftId);

  return (
    <Dialog
      open={showGeneratedCourseDialog}
      onOpenChange={setShowGeneratedCourseDialog}
    >
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Generated Course</DialogTitle>
        </DialogHeader>
        <Textarea
          readOnly
          value={
            data
              ? JSON.stringify(data, null, 2)
              : "Here is your generated schema"
          }
          className="min-h-96 max-h-96 overflow-y-scroll maxresize-none"
        />
      </DialogContent>
    </Dialog>
  );
};

interface ExportToLmsDialogProps {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  draftId: string;
}

const ExportToLmsDialog = ({
  open,
  onOpenChange,
  draftId,
}: ExportToLmsDialogProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { mutateAsync: exportToLMS } = useExportLms();

  const handleConfirm = async () => {
    await exportToLMS({ draftId, email, password });
    setEmail("");
    setPassword("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export to LMS</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button variant="default" onClick={handleConfirm}>
              Export
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

type DraftMessage = { type: string; content: string };

export const DraftPage = () => {
  const { draftId } = useParams();

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ["draftMessages", { draftId }] });
  }, [draftId]);

  const { data: draft } = useDraft(draftId);
  const {
    data: draftMessages,
    error,
    isLoading,
  } = useCurrentDraftMessages(draftId);
  const navigate = useNavigate();

  const [exportLMS, setExportLMS] = useState(false);

  const {
    messages,
    input,
    setMessages,
    handleInputChange,
    handleSubmit,
    status,
  } = useChat({
    api: `${import.meta.env.VITE_API_URL}/api/v1/ai/chat/${draftId}`,
    credentials: "include",
    body: {
      draftId,
    },
    fetch: async (url, options) => {
      const body = JSON.parse(options?.body as string);
      return fetch(url, {
        ...options,
        body: JSON.stringify({
          message: body.messages[body.messages.length - 1]?.content || "",
        }),
      });
    },
  });

  const [showGeneratedCourseDialog, setShowGeneratedCourseDialog] =
    useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages(
      (draftMessages as DraftMessage[])?.map((msg) => ({
        id: Math.random().toString(),
        role: msg.type === "ai" ? "assistant" : "user",
        content: msg.content,
      })) || [],
    );
  }, [draftMessages, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (error) {
    navigate("/");
  }

  const isSubmitted = status === "submitted" || status === "streaming";

  return (
    <>
      <h1 className="text-2xl font-bold">{draft?.draftName}</h1>
      <div className="flex-1 flex flex-col justify-start items-center overflow-y-scroll h-full max-h-4/6 gap-2">
        {!isLoading &&
          messages.map((msg, idx) => (
            <ChatMessage
              key={idx}
              isAI={msg.role === "assistant"}
              message={msg.content}
            />
          ))}

        {isSubmitted && (
          <ChatMessage isAI={true} message={<AgentTypingAnimation />} />
        )}
        <div ref={messagesEndRef} />
      </div>

      <SchemaDialog
        showGeneratedCourseDialog={showGeneratedCourseDialog}
        setShowGeneratedCourseDialog={setShowGeneratedCourseDialog}
        draftId={draftId ?? ""}
      />

      <ExportToLmsDialog
        open={exportLMS}
        onOpenChange={setExportLMS}
        draftId={draftId ?? ""}
      />

      <div className="flex flex-col w-full border-t border-sidebar-border p-4 bg-background gap-2">
        <form className="flex gap-2" onSubmit={handleSubmit}>
          <Input
            type="text"
            placeholder="Message AI agent..."
            value={input}
            onChange={handleInputChange}
            className="flex-1 bg-input border border-sidebar-border rounded-full px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <Button
            type="submit"
            className="bg-primary text-primary-foreground rounded-full px-4 py-2 font-medium hover:bg-secondary cursor-pointer transition-colors"
          >
            Send
          </Button>
        </form>

        <div className="flex justify-center gap-2 mt-2">
          <ButtonGroup>
            <Button
              variant="outline"
              onClick={() => setExportLMS(true)}
              className="bg-foreground text-background rounded-2xl px-4 py-2 font-medium hover:bg-secondary cursor-pointer transition-colors"
            >
              Export to LMS
            </Button>
            <Button
              variant="outline"
              className="bg-foreground text-background rounded-2xl px-4 py-2 font-medium hover:bg-secondary cursor-pointer transition-colors"
              onClick={() => setShowGeneratedCourseDialog(true)}
            >
              View generated course
            </Button>
          </ButtonGroup>
        </div>
      </div>
    </>
  );
};
