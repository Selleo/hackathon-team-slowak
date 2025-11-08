import { queryOptions, useQuery } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";
import { useEffect } from "react";

export const currentUserQueryOptions = queryOptions({
  queryKey: ["currentUser"],
  queryFn: async () => {
    const response = await ApiClient.api.getUserMeApiV1AuthMeGet();
    return response.data;
  },
});

export const useCurrentUser = () => {
  const userQuery = useQuery(currentUserQueryOptions);
  const { setCurrentUser } = useCurrentUserStore();
  const { data: currentUser, isSuccess } = userQuery;

  useEffect(() => {
    if (isSuccess && currentUser) {
      setCurrentUser(currentUser);
    }
  }, [isSuccess, currentUser, setCurrentUser]);

  return userQuery;
};
