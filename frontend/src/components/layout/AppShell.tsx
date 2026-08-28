"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { users } from "@/lib/api";
import { useTheme } from "@/lib/theme";
import {
  LayoutDashboard, BookOpen, Code2, Brain, Sparkles,
  Trophy, BookMarked, Settings, LogOut, Menu, X, Bell,
  GraduationCap, Sun, Moon, User, ChevronLeft,
  ClipboardList, FolderKanban, BarChart3, MessagesSquare,
} from "lucide-react";
import { useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { PageLoader } from "@/components/ui/States";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/courses", label: "Courses", icon: BookOpen },
  { href: "/practice", label: "Practice", icon: Code2 },
  { href: "/quizzes", label: "Quizzes", icon: ClipboardList },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/revision", label: "Revision", icon: Brain },
  { href: "/ai", label: "AI Assistant", icon: Sparkles },
];

const secondaryItems = [
  { href: "/achievements", label: "Achievements", icon: Trophy },
  { href: "/leaderboard", label: "Leaderboard", icon: BarChart3 },
  { href: "/discussions", label: "Discussions", icon: MessagesSquare },
  { href: "/bookmarks", label: "Bookmarks", icon: BookMarked },
  { href: "/settings", label: "Settings", icon: Settings },
];

const adminItems = [
  { href: "/admin/ai", label: "AI Course Gen", icon: Sparkles },
];

// Pages that require a signed-in user. Course browsing stays public so
// prospective students can explore the catalog before enrolling.
const protectedPathnames = [
  "/dashboard",
  "/practice",
  "/quizzes",
  "/projects",
  "/revision",
  "/ai",
  "/achievements",
  "/leaderboard",
  "/discussions",
  "/bookmarks",
  "/notifications",
  "/settings",
  "/profile",
  "/admin",
];

function isProtected(pathname: string): boolean {
  if (
    protectedPathnames.some(
      (p) => pathname === p || pathname.startsWith(p + "/")
    )
  ) {
    return true;
  }
  // Learning interface requires a session (browsing a course page does not).
  return /\/courses\/[^/]+\/learn($|\/)/.test(pathname);
}

const navLinkBase =
  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150";

function NavLink({
  href,
  label,
  icon: Icon,
  isActive,
  onNavigate,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  isActive: boolean;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      aria-current={isActive ? "page" : undefined}
      className={cn(
        navLinkBase,
        isActive
          ? "bg-coral-50 text-coral-700 dark:bg-coral-500/10 dark:text-coral-400"
          : "text-ink-secondary dark:text-ink-tertiary hover:text-ink dark:hover:text-ink hover:bg-surface-tertiary dark:hover:bg-white/5"
      )}
    >
      <Icon className={cn("h-5 w-5 flex-shrink-0", isActive && "text-coral-600 dark:text-coral-400")} />
      {label}
      {isActive && <ChevronLeft className="h-4 w-4 ml-auto rotate-180 text-coral-500" aria-hidden="true" />}
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const { resolvedTheme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { data: unreadNotifs } = useQuery({
    queryKey: ["unread-notifications"],
    queryFn: () => users.getNotifications(1, true),
    enabled: isAuthenticated,
  });
  const unreadCount = unreadNotifs?.total ?? 0;

  const isAuthPage = pathname === "/" || pathname === "/login" || pathname === "/signup";

  const requiresAuth = isProtected(pathname);

  // Client-side session guard (replaces the old broken cookie-based middleware).
  useEffect(() => {
    if (isLoading) return;
    if (requiresAuth && !isAuthenticated) {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, requiresAuth, isAuthenticated, pathname, router]);

  const handleLogout = useCallback(() => {
    logout();
  }, [logout]);

  // Landing page / auth pages get no shell
  if (isAuthPage) return <>{children}</>;

  // While the session is resolving (or a redirect is pending), avoid flashing
  // protected content at unauthenticated visitors.
  if (requiresAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen bg-surface-secondary dark:bg-night-600 flex items-center justify-center">
        <PageLoader label="Checking your session" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 transition-colors duration-300">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[60] focus:px-4 focus:py-2 focus:rounded-lg focus:bg-coral-500 focus:text-night-600 focus:text-sm focus:font-medium"
      >
        Skip to main content
      </a>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-full w-64 bg-surface dark:bg-night-500 border-r border-border dark:border-white/5",
          "transform transition-transform duration-200 ease-in-out",
          "lg:translate-x-0 shadow-none",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
        aria-label="Primary navigation"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-border dark:border-white/5">
            <Link href="/dashboard" className="flex items-center gap-2.5 group">
              <div className="h-8 w-8 rounded-lg bg-ink dark:bg-paper-50 flex items-center justify-center border border-border dark:border-white/10">
                <GraduationCap className="h-4 w-4 text-coral-500" aria-hidden="true" />
              </div>
              <span className="font-display font-bold text-lg text-ink dark:text-ink tracking-tight">
                DSir <span className="font-mono text-[10px] uppercase tracking-eyebrow text-coral-500 align-middle ml-0.5">Academy</span>
              </span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1.5 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-tertiary"
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
            <p className="px-3 pt-1 pb-2 text-2xs font-mono font-bold text-ink-tertiary uppercase tracking-eyebrow">Learn</p>
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <NavLink
                  key={item.href}
                  href={item.href}
                  label={item.label}
                  icon={item.icon}
                  isActive={isActive}
                  onNavigate={() => setSidebarOpen(false)}
                />
              );
            })}

            <div className="pt-4 pb-2">
              <div className="h-px bg-border dark:bg-white/5 mx-3" />
            </div>

            <p className="px-3 pt-1 pb-2 text-2xs font-mono font-bold text-ink-tertiary uppercase tracking-eyebrow">Library</p>
            {secondaryItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <NavLink
                  key={item.href}
                  href={item.href}
                  label={item.label}
                  icon={item.icon}
                  isActive={isActive}
                  onNavigate={() => setSidebarOpen(false)}
                />
              );
            })}

            {/* Admin section */}
            {user && (user.role === "admin" || user.role === "superadmin") && (
              <>
                <div className="pt-4 pb-2">
                  <div className="h-px bg-border dark:bg-white/5 mx-3" />
                  <p className="px-3 pt-3 text-2xs font-mono font-bold text-coral-600 dark:text-coral-400 uppercase tracking-eyebrow">Admin</p>
                </div>
                {adminItems.map((item) => {
                  const isActive = pathname.startsWith(item.href);
                  return (
                    <NavLink
                      key={item.href}
                      href={item.href}
                      label={item.label}
                      icon={item.icon}
                      isActive={isActive}
                      onNavigate={() => setSidebarOpen(false)}
                    />
                  );
                })}
              </>
            )}
          </nav>

          {/* User */}
          {user && (
            <div className="p-3 border-t border-border dark:border-white/5">
              <div className="flex items-center gap-3 px-3 py-2 rounded-xl">
                <div className="h-9 w-9 rounded-full bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center text-coral-500 font-semibold text-sm flex-shrink-0">
                  {user.display_name?.[0]?.toUpperCase() || "U"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink dark:text-ink truncate">{user.display_name}</p>
                  <p className="text-xs text-ink-tertiary truncate">{user.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-tertiary hover:text-red-500 transition-colors"
                  title="Sign out"
                  aria-label="Sign out"
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
        <header className="sticky top-0 z-30 h-16 bg-surface/85 dark:bg-night-500/85 backdrop-blur-xl border-b border-border dark:border-white/5 flex items-center justify-between px-4 lg:px-8 gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink dark:text-ink"
            aria-label="Open navigation"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-1">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary dark:text-ink-tertiary transition-colors"
              title={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
              aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {resolvedTheme === "dark" ? (
                <Sun className="h-4.5 w-4.5" aria-hidden="true" />
              ) : (
                <Moon className="h-4.5 w-4.5" aria-hidden="true" />
              )}
            </button>

            <Link
              href="/notifications"
              className="relative p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary dark:text-ink-tertiary transition-colors"
              aria-label={unreadCount > 0 ? `${unreadCount} unread notifications` : "Notifications"}
            >
              <Bell className="h-4.5 w-4.5" aria-hidden="true" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-coral-500 text-night-600 text-[10px] font-bold flex items-center justify-center ring-2 ring-surface dark:ring-night-500">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Link>
            <Link
              href="/profile"
              className="p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary dark:text-ink-tertiary transition-colors"
              aria-label="Your profile"
            >
              <User className="h-4.5 w-4.5" aria-hidden="true" />
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main id="main-content" className="flex-1 p-4 lg:p-8 animate-fade-in">{children}</main>
      </div>
    </div>
  );
}
