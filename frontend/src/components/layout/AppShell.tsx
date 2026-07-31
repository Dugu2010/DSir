"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import {
  LayoutDashboard, BookOpen, Code2, Brain, Sparkles,
  Trophy, BookMarked, Settings, LogOut, Menu, X, Bell,
  GraduationCap, ChevronRight, User,
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
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isAuthPage = pathname === "/" || pathname === "/login" || pathname === "/signup";

  // Landing page / auth pages get no shell
  if (isAuthPage) return <>{children}</>;

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-[#0a0a0b]">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-full w-64 bg-surface dark:bg-[#111113] border-r border-border",
          "transform transition-transform duration-200 ease-in-out",
          "lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-border">
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-xl bg-brand-600 flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-lg text-ink">DSir</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1.5 rounded-lg hover:bg-surface-secondary"
            >
              <X className="h-5 w-5 text-ink-secondary" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                  pathname === item.href || pathname.startsWith(item.href + "/")
                    ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400"
                    : "text-ink-secondary hover:text-ink hover:bg-surface-secondary"
                )}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {item.label}
              </Link>
            ))}

            <div className="pt-4 pb-2">
              <div className="h-px bg-border mx-3" />
            </div>

            {secondaryItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                  pathname === item.href
                    ? "bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400"
                    : "text-ink-secondary hover:text-ink hover:bg-surface-secondary"
                )}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {item.label}
              </Link>
            ))}
          </nav>

          {/* User */}
          {user && (
            <div className="p-3 border-t border-border">
              <div className="flex items-center gap-3 px-3 py-2">
                <div className="h-9 w-9 rounded-full bg-brand-100 dark:bg-brand-900 flex items-center justify-center text-brand-700 dark:text-brand-300 font-semibold text-sm flex-shrink-0">
                  {user.display_name?.[0]?.toUpperCase() || "U"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">{user.display_name}</p>
                  <p className="text-xs text-ink-tertiary truncate">{user.email}</p>
                </div>
                <button
                  onClick={() => logout()}
                  className="p-1.5 rounded-lg hover:bg-surface-secondary text-ink-tertiary hover:text-red-600 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-16 bg-surface/80 dark:bg-[#111113]/80 backdrop-blur-xl border-b border-border flex items-center justify-between px-4 lg:px-8">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-surface-secondary"
          >
            <Menu className="h-5 w-5 text-ink" />
          </button>

          <div className="flex items-center gap-3 ml-auto">
            <Link href="/notifications" className="relative p-2 rounded-lg hover:bg-surface-secondary text-ink-secondary">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500" />
            </Link>
            <Link href="/profile" className="p-2 rounded-lg hover:bg-surface-secondary text-ink-secondary">
              <User className="h-5 w-5" />
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
