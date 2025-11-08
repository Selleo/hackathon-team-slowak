import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserResponse } from "@/api/generated-api.ts";

type CurrentUserStore = {
  currentUser?: UserResponse;
  setCurrentUser: (value: UserResponse | undefined) => void;
};

export const useCurrentUserStore = create<CurrentUserStore>()(
  persist(
    (set) => ({
      currentUser: undefined,
      setCurrentUser: (value) => set({ currentUser: value }),
    }),
    {
      name: "current-user-storage",
    },
  ),
);
