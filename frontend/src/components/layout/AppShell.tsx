"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import {
  LayoutDashboard, BookOpen, Code2, Brain, Sparkles,
  Trophy, BookMarked, Settings, LogOut, Menu, X, Bell,
  GraduationCap, Sun, Moon, User, ChevronLeft,
} from "lucide-react";
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/Button";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/courses", label: "Courses", icon: BookOpen },
  { href: "/practice", label: "Practice", icon: Code2 },
  { href: "/revision", label: "Revision", icon: Brain },
  { href: "/ai", label: "AI Assistant", icon: Sparkles },
];

const secondaryItems = [
  { href: "/achievements", label: "Achievements", icon: Trophy },
  { href: "/bookmarks", label: "Bookmarks", icon: BookMarked },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const { resolvedTheme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isAuthPage = pathname === "/" || pathname === "/login" || pathname === "/signup";

  // Landing page / auth pages get no shell
  if (isAuthPage) return <>{children}</>;

  return (
    <div className="min-h-screen bg-[#fafbff] dark:bg-[#0a0a0f] transition-colors duration-200">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-[#0d0d13] border-r border-[#e8ecf1] dark:border-white/5",
          "transform transition-transform duration-200 ease-in-out",
          "lg:translate-x-0 shadow-sm lg:shadow-none",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-[#e8ecf1] dark:border-white/5">
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-sm shadow-brand-500/20">
                <GraduationCap className="h-4.5 w-4.5 text-white" />
              </div>
              <span className="font-bold text-lg text-[#1a1d2e] dark:text-white tracking-tight">DSir</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1.5 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280]"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group",
                    isActive
                      ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400 shadow-sm"
                      : "text-[#6b7280] dark:text-[#8b8fa3] hover:text-[#1a1d2e] dark:hover:text-white hover:bg-[#f1f3f5] dark:hover:bg-white/5"
                  )}
                >
                  <item.icon className={cn("h-5 w-5 flex-shrink-0 transition-colors", isActive && "text-brand-600 dark:text-brand-400")} />
                  {item.label}
                  {isActive && <ChevronLeft className="h-4 w-4 ml-auto rotate-180 text-brand-400" />}
                </Link>
              );
            })}

            <div className="pt-4 pb-2">
              <div className="h-px bg-[#e8ecf1] dark:bg-white/5 mx-3" />
            </div>

            {secondaryItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                    isActive
                      ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                      : "text-[#6b7280] dark:text-[#8b8fa3] hover:text-[#1a1d2e] dark:hover:text-white hover:bg-[#f1f3f5] dark:hover:bg-white/5"
                  )}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* User */}
          {user && (
            <div className="p-3 border-t border-[#e8ecf1] dark:border-white/5">
              <div className="flex items-center gap-3 px-3 py-2 rounded-xl">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0 shadow-sm">
                  {user.display_name?.[0]?.toUpperCase() || "U"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[#1a1d2e] dark:text-white truncate">{user.display_name}</p>
                  <p className="text-xs text-[#9ca3af] dark:text-[#6b7280] truncate">{user.email}</p>
                </div>
                <button
                  onClick={() => logout()}
                  className="p-1.5 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#9ca3af] hover:text-red-500 transition-colors"
                  title="Sign out"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-[#0d0d13]/80 backdrop-blur-xl border-b border-[#e8ecf1] dark:border-white/5 flex items-center justify-between px-4 lg:px-8 gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#1a1d2e] dark:text-white"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-1">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] transition-colors"
              title={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {resolvedTheme === "dark" ? (
                <Sun className="h-4.5 w-4.5" />
              ) : (
                <Moon className="h-4.5 w-4.5" />
              )}
            </button>

            <Link href="/notifications" className="relative p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] transition-colors">
              <Bell className="h-4.5 w-4.5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-[#0d0d13]" />
            </Link>
            <Link href="/profile" className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] transition-colors">
              <User className="h-4.5 w-4.5" />
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 animate-fade-in">{children}</main>
      </div>
    </div>
  );
}
