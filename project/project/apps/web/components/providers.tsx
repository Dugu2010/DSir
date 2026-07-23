"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState } from "react";
import { queryClient } from "@/lib/query-client";
import { AuthInitializer } from "./auth-initializer";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => queryClient);

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryClientProvider client={client}>
        <AuthInitializer>{children}</AuthInitializer>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
