"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";

type Theme = "light" | "dark" | "system";

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: "system",
  resolvedTheme: "light",
  setTheme: () => {},
  toggleTheme: () => {},
});

function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("system");
  const [resolvedTheme, setResolved] = useState<"light" | "dark">("light");

  const applyTheme = useCallback((t: "light" | "dark") => {
    setResolved(t);
    document.documentElement.classList.toggle("dark", t === "dark");
    localStorage.setItem("theme", t);
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    const initial = stored || "system";
    setThemeState(initial);
    const resolved = initial === "system" ? getSystemTheme() : initial;
    applyTheme(resolved);
  }, [applyTheme]);

  useEffect(() => {
    if (theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => applyTheme(getSystemTheme());
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [theme, applyTheme]);

  const setTheme = useCallback(
    (t: Theme) => {
      setThemeState(t);
      const resolved = t === "system" ? getSystemTheme() : t;
      applyTheme(resolved);
    },
    [applyTheme]
  );

  const toggleTheme = useCallback(() => {
    const next = resolvedTheme === "dark" ? "light" : "dark";
    setThemeState(next);
    applyTheme(next);
  }, [resolvedTheme, applyTheme]);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
