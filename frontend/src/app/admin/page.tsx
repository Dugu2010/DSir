"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { admin as adminApi } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import {
  Sparkles, Users, ArrowRight, Shield, Layers, GraduationCap,
  CheckCircle2, CalendarDays, Activity,
} from "lucide-react";

interface AdminStats {
  total_users: number;
  total_courses: number;
  total_enrollments: number;
  total_completions: number;
  active_today: number;
  new_users_week: number;
}

const tools = [
  {
    title: "AI Import",
    desc: "Generate courses and lessons with AI.",
    href: "/admin/ai",
    icon: Sparkles,
    color: "bg-coral-500/10 text-coral-600 dark:text-coral-400 border-coral-500/25",
  },
];

export default function AdminPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const isAdmin = user?.role === "admin" || user?.role === "superadmin";

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.replace("/login?redirect=/admin");
    }
  }, [isLoading, isAdmin, router]);

  const { data: stats, isLoading: statsLoading, isError: statsError } = useQuery<AdminStats>({
    queryKey: ["admin-dashboard"],
    queryFn: () => adminApi.getDashboard(),
    enabled: !isLoading && isAdmin,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-secondary dark:bg-night-600 flex items-center justify-center">
        <div className="h-8 w-8 border-2 border-coral-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user || !isAdmin) return null;

  const overview = [
    { label: "Users", value: stats?.total_users, icon: Users },
    { label: "Courses", value: stats?.total_courses, icon: Layers },
    { label: "Enrollments", value: stats?.total_enrollments, icon: GraduationCap },
    { label: "Completions", value: stats?.total_completions, icon: CheckCircle2 },
    { label: "Active today", value: stats?.active_today, icon: Activity },
    { label: "New users · 7 days", value: stats?.new_users_week, icon: CalendarDays },
  ];

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-8">
        <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-6 sm:p-8">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400 flex items-center gap-2">
            <Shield className="h-3.5 w-3.5" /> {"// "}No. 19 · Administration
          </p>
          <h1 className="font-display text-3xl md:text-4xl font-medium tracking-tight text-ink mt-3">Admin Panel</h1>
          <p className="mt-2 text-ink-secondary leading-relaxed max-w-xl">
            Live platform stats and AI-powered content generation.
          </p>
        </header>

        <section className="rounded-xl border border-border dark:border-white/10 overflow-hidden">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-px bg-border dark:bg-white/10">
            {overview.map((item) => (
              <div key={item.label} className="bg-surface dark:bg-night-500 p-5 sm:p-6">
                <div className="flex items-center gap-2 text-ink-tertiary">
                  <item.icon className="h-3.5 w-3.5" aria-hidden="true" />
                  <p className="font-mono text-[10px] uppercase tracking-[0.16em]">{item.label}</p>
                </div>
                {statsLoading ? (
                  <span className="mt-3 block h-8 w-14 rounded bg-surface-tertiary dark:bg-white/10 animate-pulse" aria-hidden="true" />
                ) : (
                  <p className="mt-3 font-display text-3xl font-medium text-ink leading-none">
                    {statsError || item.value === undefined ? "—" : formatNumber(item.value)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>

        {tools.map((tool) => (
          <Link key={tool.href} href={tool.href}>
            <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-6 hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-colors group cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className={`h-10 w-10 rounded-lg border flex items-center justify-center ${tool.color}`}>
                  <tool.icon className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-ink-tertiary group-hover:text-coral-500 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h3 className="font-display text-lg font-medium text-ink">{tool.title}</h3>
              <p className="mt-1.5 text-sm text-ink-secondary">{tool.desc}</p>
            </div>
          </Link>
        ))}

        <div className="p-6 rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 text-ink-tertiary" />
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">{"// "}Session</p>
          </div>
          <p className="text-sm text-ink-secondary">
            Signed in as <span className="text-ink font-medium">{user.display_name || user.username}</span>{" "}
            with administrator access. Use the AI Import tool to generate new courses from a topic description.
          </p>
        </div>
      </div>
    </div>
  );
}
