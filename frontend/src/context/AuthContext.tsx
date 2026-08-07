import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { authApi, type LoginPayload, type RegisterPayload } from "@/lib/auth/authApi";
import { tokenStorage } from "@/lib/auth/tokenStorage";
import { sessionExpiredBus } from "@/lib/auth/sessionExpiredBus";
import type { User } from "@/types/entities";

type SessionStatus = "restoring" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  user: User | null;
  status: SessionStatus;
  login: (payload: LoginPayload, rememberMe: boolean) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<SessionStatus>("restoring");
  const queryClient = useQueryClient();

  const clearSession = useCallback(() => {
    tokenStorage.clear();
    queryClient.clear();
    setUser(null);
    setStatus("unauthenticated");
  }, [queryClient]);

  // Registered once so the Axios interceptor can force a logout when a
  // refresh attempt fails — this is what turns a truly expired session
  // into a redirect to /login instead of silently-failing requests.
  useEffect(() => {
    sessionExpiredBus.subscribe(clearSession);
  }, [clearSession]);

  // On first load: if a refresh token exists, ask the backend who we are.
  // The Axios interceptor transparently refreshes a stale access token
  // as part of that request if needed.
  useEffect(() => {
    async function restore() {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        setStatus("unauthenticated");
        return;
      }
      try {
        const restoredUser = await authApi.me();
        setUser(restoredUser);
        setStatus("authenticated");
      } catch {
        clearSession();
      }
    }
    restore();
  }, [clearSession]);

  const login = useCallback(async (payload: LoginPayload, rememberMe: boolean): Promise<User> => {
    const response = await authApi.login(payload);
    tokenStorage.setTokens(response.access, response.refresh, rememberMe);
    setUser(response.user);
    setStatus("authenticated");
    return response.user;
  }, []);

  const register = useCallback(async (payload: RegisterPayload): Promise<User> => {
    const response = await authApi.register(payload);
    // Tokens are issued immediately so the new account lands in a real
    // session; privileged actions (donating, campaign creation) stay
    // gated server-side on email_verified per Architecture Freeze v1.0.
    tokenStorage.setTokens(response.access, response.refresh, false);
    setUser(response.user);
    setStatus("authenticated");
    return response.user;
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    const refreshToken = tokenStorage.getRefreshToken();
    try {
      if (refreshToken) await authApi.logout(refreshToken);
    } catch {
      // Best-effort server-side blacklist — local logout proceeds
      // regardless.
    } finally {
      clearSession();
    }
  }, [clearSession]);

  return (
    <AuthContext.Provider value={{ user, status, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
