"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/hooks/use-auth";
import { fetchMe, clearAuthCookies } from "@/lib/axios";

export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { setUser, setIsLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    async function init() {
      if (!isAuthenticated) {
        setIsLoading(false);
        return;
      }

      try {
        const user = await fetchMe();
        setUser(user);
      } catch {
        clearAuthCookies();
        setUser(null);
      }
    }

    init();
  }, [isAuthenticated, setUser, setIsLoading]);

  return <>{children}</>;
}
