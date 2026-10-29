"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader } from "@/components/ui/States";
import { useQuery } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { formatNumber, formatDate, levelProgress } from "@/lib/utils";
import {
  User, Mail, Calendar, Award, BookOpen, Code2, Flame, Trophy,
  Settings, ArrowRight,
} from "lucide-react";

const dossierLinks = [
  { href: "/profile/certificates", label: "Certificates", desc: "Earned credentials", icon: Award },
  { href: "/achievements", label: "Achievements", desc: "Milestone badges", icon: Trophy },
  { href: "/settings", label: "Settings", desc: "Account preferences", icon: Settings },
];

export default function ProfilePage() {
  const { user } = useAuth();

  const { data: stats } = useQuery({
    queryKey: ["user-stats"],
    queryFn: () => users.getStats(),
    enabled: !!user,
  });

  if (!user) return <PageLoader />;

  const progress = stats ? levelProgress(stats.total_xp, stats.current_level) : 0;

  const metrics = stats
    ? [
        { label: "Lessons completed", value: stats.lessons_completed, icon: BookOpen },
        { label: "Exercises solved", value: stats.exercises_completed, icon: Code2 },
        { label: "Projects shipped", value: stats.projects_completed, icon: Award },
        { label: "Longest streak", value: `${stats.longest_streak}d`, icon: Flame },
      ]
    : [];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 08 · Student cockpit
          </p>
          <div className="flex flex-col sm:flex-row sm:items-start gap-5 mt-4">
            <div className="h-16 w-16 rounded-lg border border-coral-500/30 bg-coral-500/10 flex items-center justify-center font-display text-2xl font-medium text-coral-600 dark:text-coral-400 shrink-0">
              {user.display_name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="font-display text-3xl md:text-4xl font-medium tracking-tight leading-[1.1] text-ink">
                  {user.display_name}
                </h1>
                {stats && (
                  <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-coral-600 dark:text-coral-400 border border-coral-500/30 bg-coral-500/5 rounded-full px-2.5 py-1 tabular-nums">
                    L{stats.current_level}
                  </span>
                )}
              </div>
              <p className="font-mono text-[11px] tracking-[0.06em] text-ink-tertiary mt-1.5 break-all">
                @{user.username} · {user.email}
              </p>
              <div className="flex flex-wrap items-center gap-3 mt-3">
                <Badge variant="outline" size="sm">{user.role}</Badge>
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary flex items-center gap-1">
                  <Calendar className="h-3 w-3" /> Joined {formatDate(user.created_at)}
                </span>
              </div>
            </div>
          </div>

          {stats && (
            <div className="mt-6">
              <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mb-1.5">
                <span>Level {stats.current_level} · {progress}% to next</span>
                <span className="tabular-nums">{formatNumber(stats.total_xp)} XP total</span>
              </div>
              <div className="h-1 rounded-full bg-surface-tertiary dark:bg-white/10 overflow-hidden" aria-hidden="true">
                <div className="h-full bg-coral-500" style={{ width: `${progress}%` }} />
              </div>
            </div>
          )}
        </div>

        {metrics.length > 0 && (
          <dl className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
            {metrics.map((metric) => (
              <div key={metric.label} className="bg-surface dark:bg-night-500 px-5 py-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary flex items-center gap-1.5">
                  <metric.icon className="h-3 w-3" /> {metric.label}
                </dt>
                <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{metric.value}</dd>
              </div>
            ))}
          </dl>
        )}
      </header>

      <section>
        <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary mb-3">
          {"// "}Account metadata
        </p>
        <Card padding="none">
          <dl className="divide-y divide-border dark:divide-white/10 text-sm">
            <div className="flex items-center justify-between gap-4 px-5 py-3.5">
              <dt className="text-ink-tertiary flex items-center gap-2">
                <Mail className="h-4 w-4" /> Email
              </dt>
              <dd className="text-ink text-right break-all">{user.email}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-5 py-3.5">
              <dt className="text-ink-tertiary flex items-center gap-2">
                <User className="h-4 w-4" /> Username
              </dt>
              <dd className="font-mono text-[13px] text-ink text-right">@{user.username}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-5 py-3.5">
              <dt className="text-ink-tertiary flex items-center gap-2">
                <Calendar className="h-4 w-4" /> Joined
              </dt>
              <dd className="text-ink text-right">{formatDate(user.created_at)}</dd>
            </div>
            <div className="flex items-center justify-between gap-4 px-5 py-3.5">
              <dt className="text-ink-tertiary flex items-center gap-2">
                <Award className="h-4 w-4" /> Role
              </dt>
              <dd>
                <Badge variant={user.role === "student" ? "default" : "info"}>{user.role}</Badge>
              </dd>
            </div>
          </dl>
        </Card>
      </section>

      <section>
        <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary mb-3">
          {"// "}Dossier index
        </p>
        <div className="grid sm:grid-cols-3 gap-3">
          {dossierLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-5 hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-colors"
            >
              <div className="flex items-center justify-between">
                <link.icon className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                <ArrowRight className="h-4 w-4 text-ink-tertiary group-hover:text-coral-600 dark:group-hover:text-coral-400 transition-colors" />
              </div>
              <p className="font-display font-medium text-ink mt-4">{link.label}</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">{link.desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
