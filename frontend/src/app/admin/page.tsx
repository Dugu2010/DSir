"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  LayoutDashboard, Sparkles, Users, BookOpen,
  ArrowRight, Shield,
} from "lucide-react";

const tools = [
  {
    title: "Dashboard",
    desc: "Overview stats — users, courses, enrollments.",
    href: "/admin",
    icon: LayoutDashboard,
    color: "bg-blue-500/10 text-blue-400",
  },
  {
    title: "AI Import",
    desc: "Generate courses and lessons with AI.",
    href: "/admin/ai",
    icon: Sparkles,
    color: "bg-coral-500/10 text-coral-400",
  },
];

export default function AdminPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "admin")) {
      router.replace("/login?redirect=/admin");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-secondary dark:bg-night-600 flex items-center justify-center">
        <div className="h-8 w-8 border-2 border-coral-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user || user.role !== "admin") return null;

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-coral-500/10 flex items-center justify-center">
            <Shield className="h-5 w-5 text-coral-500" />
          </div>
          <div>
            <p className="eyebrow">Administration</p>
            <h1 className="font-display text-3xl font-semibold text-ink">Admin Panel</h1>
          </div>
        </div>
        <p className="mt-3 text-ink-secondary leading-relaxed max-w-xl">
          Manage courses, users, and AI-powered content generation.
        </p>

        <div className="mt-10 grid sm:grid-cols-2 gap-4">
          {tools.map((tool) => (
            <Link key={tool.href} href={tool.href}>
              <div className="rounded-2xl border border-border dark:border-white/5 bg-surface dark:bg-night-500 p-6 hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-all group cursor-pointer">
                <div className="flex items-center justify-between mb-4">
                  <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${tool.color}`}>
                    <tool.icon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-4 w-4 text-ink-tertiary group-hover:text-coral-500 group-hover:translate-x-0.5 transition-all" />
                </div>
                <h3 className="font-display text-lg font-semibold text-ink">{tool.title}</h3>
                <p className="mt-1.5 text-sm text-ink-secondary">{tool.desc}</p>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-8 p-6 rounded-2xl border border-border dark:border-white/5 bg-surface dark:bg-night-500">
          <div className="flex items-center gap-3 mb-2">
            <Users className="h-5 w-5 text-ink-tertiary" />
            <h3 className="font-display font-semibold text-ink">Quick Stats</h3>
          </div>
          <p className="text-sm text-ink-secondary">
            Signed in as <span className="text-ink font-medium">{user.display_name || user.username}</span>{" "}
            with admin privileges. Use the AI Import tool to generate new courses from a topic description.
          </p>
        </div>
      </div>
    </div>
  );
}
