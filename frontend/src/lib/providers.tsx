"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/lib/auth-store";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  const { initialize } = useAuthStore();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    initialize().finally(() => setReady(true));
    const handler = () => { window.location.href = "/login"; };
    window.addEventListener("auth:logout", handler);
    return () => window.removeEventListener("auth:logout", handler);
  }, [initialize]);

  return (
    <QueryClientProvider client={queryClient}>
      {ready ? children : (
        <div className="min-h-screen flex items-center justify-center">
          <div className="h-8 w-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            borderRadius: "12px",
            padding: "12px 16px",
            fontSize: "14px",
          },
        }}
      />
    </QueryClientProvider>
  );
}
