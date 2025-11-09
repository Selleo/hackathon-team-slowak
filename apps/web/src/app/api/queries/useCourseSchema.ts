import { queryOptions, useQuery } from "@tanstack/react-query";
import { ApiClient } from "@/app/api/api-client.ts";

export const courseSchemaQueryOptions = (draftId?: string) =>
  queryOptions({
    enabled: !!draftId,
    queryKey: ["course-schema", { courseSchemaQueryOptions }],
    queryFn: async () => {
      const response =
        await ApiClient.api.getCourseSchemaApiV1AiCourseSchemaDraftIdGet(
          draftId ?? "",
        );
      return response.data;
    },
  });

export const useCourseSchema = (draftId?: string) => {
  return useQuery(courseSchemaQueryOptions(draftId));
};
