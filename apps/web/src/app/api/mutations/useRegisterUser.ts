import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ApiClient } from "@/app/api/api-client.ts";
import { toast } from "sonner";
import type { UserRegister } from "@/app/api/generated-api.ts";

export default function useRegisterUser() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (options: UserRegister) => {
      const response =
        await ApiClient.api.registerApiV1AuthRegisterPost(options);
      return response.data;
    },
    onSuccess: () => {
      toast.success("You've been successfully registered! Please log in.");
      navigate("/login");
    },
    onError: () => {
      toast.error("Registration failed. Please try again.");
    },
  });
}
