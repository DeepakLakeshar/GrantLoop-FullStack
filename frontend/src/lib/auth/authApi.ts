import { apiClient } from "@/lib/api/client";
import type { User, UserRole } from "@/types/entities";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  role: Exclude<UserRole, "admin">; // admin accounts are never publicly creatable
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export const authApi = {
  async login(payload: LoginPayload): Promise<LoginResponse> {
    const { data } = await apiClient.post<LoginResponse>("/auth/login/", payload);
    return data;
  },

  async register(payload: RegisterPayload): Promise<LoginResponse> {
    const { data } = await apiClient.post<LoginResponse>("/auth/register/", payload);
    return data;
  },

  async logout(refreshToken: string): Promise<void> {
    // Best-effort — blacklists the refresh token server-side per
    // SIMPLE_JWT's BLACKLIST_AFTER_ROTATION setting. Local session
    // clearing must not depend on this succeeding.
    await apiClient.post("/auth/logout/", { refresh: refreshToken });
  },

  async me(): Promise<User> {
    const { data } = await apiClient.get<User>("/auth/me/");
    return data;
  },

  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post("/auth/password-reset/", { email });
  },

  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    await apiClient.post("/auth/password-reset/confirm/", { token, new_password: newPassword });
  },
};
