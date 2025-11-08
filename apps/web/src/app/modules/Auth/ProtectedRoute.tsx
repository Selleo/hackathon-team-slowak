import { type ReactElement, useEffect } from "react";
import { useCurrentUser } from "@/app/api/queries/useCurrentUser.ts";
import { useNavigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: ReactElement }) {
  const navigate = useNavigate();
  const { data: currentUser, isLoading } = useCurrentUser();

  useEffect(() => {
    if (!isLoading && !currentUser) {
      navigate("/login");
    }
  }, [isLoading, currentUser, navigate]);

  if (isLoading || !currentUser) {
    return null;
  }

  return children;
}
