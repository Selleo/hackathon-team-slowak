import { queryOptions, useQuery } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";

export const draftQueryOptions = (draftId?: string) =>
  queryOptions({
    enabled: !!draftId,
    queryKey: ["draft", { draftId }],
    queryFn: async () => {
      const response = await ApiClient.api.getDraftApiV1DraftDraftIdGet(
        draftId ?? "",
      );
      return response.data;
    },
  });

export const useDraft = (draftId?: string) => {
  return useQuery(draftQueryOptions(draftId));
};
