import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";
import type { CreateDraftRequestBody } from "@/app/api/generated-api.ts";

export default function useCreateDraft() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (options: CreateDraftRequestBody) => {
      const response = await ApiClient.api.createDraftApiV1DraftPost(options);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success("You've created new draft!");
      console.log(data);
      navigate(`/draft/${data.id}`);
    },
    onError: () => {
      toast.error("Creation failed. Please try again.");
    },
  });
}
