import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";
import type { UserLogin } from "@/app/api/generated-api.ts";

export type ExportLMSOptions = {
  draftId: string;
  email: string;
  password: string;
}

export default function useExportLms() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (options: ExportLMSOptions) => {
      const response = await ApiClient.api.(options);
      return response.data;
    },
    onSuccess: () => {
      toast.success("You've been successfully logged in!");
      navigate("/home");
    },
    onError: () => {
      toast.error("Login failed. Please check your credentials and try again.");
    },
  });
}
