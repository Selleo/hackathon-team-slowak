import { queryOptions, useQuery } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";

export const draftsQueryOptions = queryOptions({
  queryKey: ["drafts"],
  queryFn: async () => {
    const response = await ApiClient.api.getAllDraftsApiV1DraftAllGet();
    return response.data;
  },
});

export const useDrafts = () => {
  return useQuery(draftsQueryOptions);
};
