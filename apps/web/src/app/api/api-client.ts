import { API } from "./generated-api";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";
import { queryClient } from "@/app/api/queryClient.ts";

export const requestManager = {
  controller: new AbortController(),

  abortAll() {
    this.controller.abort();
    this.controller = new AbortController();
  },
};

export const ApiClient = new API({
  baseURL: import.meta.env.VITE_API_URL,
  secure: true,
  withCredentials: true,
});

ApiClient.instance.interceptors.request.use((config) => {
  const isAuthEndpoint =
    config.url?.includes("/Login") || config.url?.includes("/Register");

  if (!isAuthEndpoint && !useCurrentUserStore.getState().currentUser) {
    config.signal = requestManager.controller.signal;
  }

  return config;
});

ApiClient.instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.config?.url?.includes("/Logout")) {
      return Promise.reject(error);
    }

    if (
      error.response?.status === 401 &&
      !error.config._retry &&
      useCurrentUserStore.getState().currentUser
    ) {
      error.config._retry = true;
      try {
        useCurrentUserStore().setCurrentUser(undefined);
        queryClient.clear();
        return ApiClient.instance(error.config);
      } catch {
        requestManager.abortAll();
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);
