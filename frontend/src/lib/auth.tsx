"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { auth as authApi } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: { email: string; username: string; display_name: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  signup: async () => {},
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setUser(null);
        localStorage.removeItem("dsir_user");
        setIsLoading(false);
        return;
      }
      const userData = await authApi.me();
      setUser(userData);
      localStorage.setItem("dsir_user", JSON.stringify(userData));
    } catch (error: any) {
      // Only an authentication failure invalidates the session. A transient
      // 429/5xx/network error must not sign the learner out or wipe tokens.
      if (error?.status === 401) {
        setUser(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("dsir_user");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Show the last known profile while the session probe runs. This avoids a
    // flash of logged-out UI during a slow or briefly failing `/auth/me`.
    try {
      const cached = localStorage.getItem("dsir_user");
      if (cached && localStorage.getItem("access_token")) {
        setUser(JSON.parse(cached) as User);
      }
    } catch {
      localStorage.removeItem("dsir_user");
    }
    refreshUser();
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    const data = await authApi.login({ email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.removeItem("dsir_user");
    await refreshUser();
    router.push("/dashboard");
  };

  const signup = async (signupData: { email: string; username: string; display_name: string; password: string }) => {
    const data = await authApi.signup(signupData);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.removeItem("dsir_user");
    await refreshUser();
    router.push("/dashboard");
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("dsir_user");
    setUser(null);
    // No explicit navigation here: AppShell's client-side guard observes the
    // now-unauthenticated session and sends protected pages to
    // `/login?redirect=...`. This avoids a race between `router.push` and the
    // guard's `router.replace`.
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: !!user, login, signup, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
