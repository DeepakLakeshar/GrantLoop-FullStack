import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { tokenStorage } from "@/lib/auth/tokenStorage";
import { normalizeAxiosError, ApiError, type DrfErrorBody } from "@/lib/api/errors";
import { sessionExpiredBus } from "@/lib/auth/sessionExpiredBus";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
});

apiClient.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Marks a request as already retried once, so the interceptor never
// loops forever if the refreshed token is itself rejected.
interface RetryableConfig extends InternalAxiosRequestConfig {
  _retried?: boolean;
}

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }
  // axios.create instance's own interceptors would recurse — use the raw
  // axios function against the same base URL instead.
  const response = await axios.post<{ access: string }>(`${BASE_URL}/auth/refresh/`, {
    refresh: refreshToken,
  });
  tokenStorage.setAccessToken(response.data.access);
  return response.data.access;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<DrfErrorBody>) => {
    const originalRequest = error.config as RetryableConfig | undefined;
    const status = error.response?.status;

    const isAuthEndpoint = originalRequest?.url?.includes("/auth/login") || originalRequest?.url?.includes("/auth/refresh");

    if (status === 401 && originalRequest && !originalRequest._retried && !isAuthEndpoint) {
      originalRequest._retried = true;
      try {
        // Multiple simultaneous 401s should trigger exactly one refresh
        // call, not one per in-flight request.
        refreshPromise ??= refreshAccessToken();
        const newAccessToken = await refreshPromise;
        refreshPromise = null;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch {
        refreshPromise = null;
        tokenStorage.clear();
        sessionExpiredBus.emit();
        return Promise.reject(new ApiError("Your session has expired. Please sign in again.", "unauthorized", 401));
      }
    }

    return Promise.reject(normalizeAxiosError(error));
  }
);
