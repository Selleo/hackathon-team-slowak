import { useMutation } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";

export type ExportLMSOptions = {
  draftId: string;
  email: string;
  password: string;
};

export default function useExportLms() {
  return useMutation({
    mutationFn: async (options: ExportLMSOptions) => {
      const response = await ApiClient.api.exportToLmsApiV1AiExportDraftIdPost(
        options.draftId,
        { email: options.email, password: options.password },
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Course successfully exported");
    },
    onError: () => {
      toast.error("Export failed.");
    },
  });
}
