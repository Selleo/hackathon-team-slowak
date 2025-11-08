import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";
import type { UserLogin } from "@/app/api/generated-api.ts";

export default function useLoginUser() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (options: UserLogin) => {
      const response = await ApiClient.api.loginApiV1AuthLoginPost(options);
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
