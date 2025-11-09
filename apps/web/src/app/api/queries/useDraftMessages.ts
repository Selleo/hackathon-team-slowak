import { queryOptions, useQuery } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";

export const draftMessagesQueryOptions = (draftId?: string) =>
  queryOptions({
    enabled: !!draftId,
    queryKey: ["draftMessages", { draftId }],
    queryFn: async () => {
      const response = await ApiClient.api.chatApiV1AiDraftIdGet(draftId ?? "");
      return response.data;
    },
  });

export const useCurrentDraftMessages = (draftId?: string) => {
  return useQuery(draftMessagesQueryOptions(draftId));
};
