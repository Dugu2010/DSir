"use client";

import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader } from "@/components/ui/States";
import { useQuery } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { formatNumber, formatDate, levelProgress } from "@/lib/utils";
import {
  User, Mail, Calendar, Award, BookOpen, Code2, Flame,
} from "lucide-react";

export default function ProfilePage() {
  const { user, logout } = useAuth();

  const { data: stats } = useQuery({
    queryKey: ["user-stats"],
    queryFn: () => users.getStats(),
    enabled: !!user,
  });

  if (!user) return <PageLoader />;

  const progress = stats ? levelProgress(stats.total_xp, stats.current_level) : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Profile header */}
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="flex items-center gap-5">
          <div className="h-20 w-20 rounded-full bg-coral-500/15 border border-coral-500/30 flex items-center justify-center text-3xl font-bold text-coral-400">
            {user.display_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div>
            <p className="eyebrow mb-1 !text-coral-400">Profile</p>
            <h1 className="font-display text-2xl font-semibold tracking-tight">{user.display_name}</h1>
            <p className="text-paper-50/60 dark:text-ink-tertiary">@{user.username}</p>
            <p className="text-paper-50/40 dark:text-ink-tertiary text-sm mt-1">{user.email}</p>
          </div>
        </div>
        {stats && (
          <div className="flex flex-wrap gap-8 mt-6 text-sm">
            <div>
              <p className="text-paper-50/40 dark:text-ink-tertiary text-xs font-mono uppercase tracking-eyebrow">Level</p>
              <p className="font-display font-bold text-lg">{stats.current_level}</p>
            </div>
            <div>
              <p className="text-paper-50/40 dark:text-ink-tertiary text-xs font-mono uppercase tracking-eyebrow">Total XP</p>
              <p className="font-display font-bold text-lg">{formatNumber(stats.total_xp)}</p>
            </div>
            <div>
              <p className="text-paper-50/40 dark:text-ink-tertiary text-xs font-mono uppercase tracking-eyebrow">Streak</p>
              <p className="font-display font-bold text-lg">{stats.current_streak} days</p>
            </div>
            <div>
              <p className="text-paper-50/40 dark:text-ink-tertiary text-xs font-mono uppercase tracking-eyebrow">Completed</p>
              <p className="font-display font-bold text-lg">{stats.lessons_completed} lessons</p>
            </div>
          </div>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid md:grid-cols-4 gap-4">
          <Card padding="sm" className="text-center">
            <BookOpen className="h-5 w-5 text-coral-600 dark:text-coral-400 mx-auto mb-1" />
            <div className="font-display text-xl font-bold text-ink">{stats.lessons_completed}</div>
            <div className="text-xs text-ink-tertiary">Lessons</div>
          </Card>
          <Card padding="sm" className="text-center">
            <Code2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 mx-auto mb-1" />
            <div className="font-display text-xl font-bold text-ink">{stats.exercises_completed}</div>
            <div className="text-xs text-ink-tertiary">Exercises</div>
          </Card>
          <Card padding="sm" className="text-center">
            <Flame className="h-5 w-5 text-orange-500 dark:text-orange-400 mx-auto mb-1" />
            <div className="font-display text-xl font-bold text-ink">{stats.longest_streak}</div>
            <div className="text-xs text-ink-tertiary">Best Streak</div>
          </Card>
          <Card padding="sm" className="text-center">
            <Award className="h-5 w-5 text-amber-500 dark:text-amber-400 mx-auto mb-1" />
            <div className="font-display text-xl font-bold text-ink">{stats.projects_completed}</div>
            <div className="text-xs text-ink-tertiary">Projects</div>
          </Card>
        </div>
      )}

      {/* Account Info */}
      <Card padding="md">
        <p className="eyebrow mb-1">Account</p>
        <h2 className="font-display text-lg font-semibold text-ink mb-4">Account Information</h2>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between py-2">
            <span className="text-ink-tertiary flex items-center gap-2">
              <Mail className="h-4 w-4" /> Email
            </span>
            <span className="text-ink">{user.email}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-t border-border">
            <span className="text-ink-tertiary flex items-center gap-2">
              <User className="h-4 w-4" /> Username
            </span>
            <span className="text-ink">@{user.username}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-t border-border">
            <span className="text-ink-tertiary flex items-center gap-2">
              <Calendar className="h-4 w-4" /> Joined
            </span>
            <span className="text-ink">{formatDate(user.created_at)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-t border-border">
            <span className="text-ink-tertiary flex items-center gap-2">
              <Award className="h-4 w-4" /> Role
            </span>
            <Badge variant={user.role === "student" ? "default" : "info"}>{user.role}</Badge>
          </div>
        </div>
      </Card>
    </div>
  );
}
