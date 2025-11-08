import { useAuthStore } from "@/app/modules/Auth/authStore";
import { API } from "./generated-api";
import { useCurrentUserStore } from "@/app/modules/Auth/useCurrentUserStore.ts";

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

  if (!isAuthEndpoint && !useAuthStore.getState().isLoggedIn) {
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
      useAuthStore.getState().isLoggedIn
    ) {
      error.config._retry = true;
      try {
        useAuthStore().setLoggedIn(false);
        useCurrentUserStore().setCurrentUser(undefined);
        return ApiClient.instance(error.config);
      } catch {
        requestManager.abortAll();
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);
