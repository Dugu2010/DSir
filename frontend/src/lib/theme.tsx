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
  theme: "dark",
  resolvedTheme: "dark",
  setTheme: () => {},
  toggleTheme: () => {},
});

function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

// DSir Academy ships with DARK as the default experience. The persisted
// default is "dark" so first-time visitors land on the calm night palette
// (the inline script in layout.tsx applies the class before first paint).
const DEFAULT_THEME: Theme = "dark";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(DEFAULT_THEME);
  const [resolvedTheme, setResolved] = useState<"light" | "dark">("dark");

  const applyTheme = useCallback((t: "light" | "dark") => {
    setResolved(t);
    document.documentElement.classList.toggle("dark", t === "dark");
  }, []);

  useEffect(() => {
    let stored: Theme | null = null;
    try {
      stored = localStorage.getItem("theme") as Theme | null;
    } catch {
      stored = null;
    }
    const initial = stored || DEFAULT_THEME;
    setThemeState(initial);
    applyTheme(initial === "system" ? getSystemTheme() : initial);
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
      try {
        localStorage.setItem("theme", t);
      } catch {
        /* storage unavailable — theme still applies for this session */
      }
      applyTheme(t === "system" ? getSystemTheme() : t);
    },
    [applyTheme]
  );

  const toggleTheme = useCallback(() => {
    const next = resolvedTheme === "dark" ? "light" : "dark";
    setThemeState(next);
    try {
      localStorage.setItem("theme", next);
    } catch {
      /* storage unavailable */
    }
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
