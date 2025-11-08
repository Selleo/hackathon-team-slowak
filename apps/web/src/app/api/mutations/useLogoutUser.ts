import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";

export default function useLogoutUser() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async () => {
      const response = await ApiClient.api.logoutApiV1AuthLogoutPost();
      return response.data;
    },
    onSuccess: () => {
      toast.success("You've been successfully logged out!");
      navigate("/login");
    },
    onError: () => {
      navigate("/home");
    },
  });
}
