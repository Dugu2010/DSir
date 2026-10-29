"use client";

import { useQuery } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { Star, Lock, Zap } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";
import type { Achievement } from "@/lib/types";

const categoryLabel: Record<string, string> = {
  learning: "Learning",
  practice: "Practice",
  streak: "Streak",
  social: "Social",
  milestone: "Milestone",
  special: "Special",
};

export default function AchievementsPage() {
  const { data, isLoading, error, refetch } = useQuery<Achievement[]>({
    queryKey: ["achievements"],
    queryFn: () => users.getAchievements(),
  });

  if (isLoading) return <PageLoader label="Loading achievements..." />;
  if (error || !data) {
    return (
      <ErrorState
        title="Failed to load achievements"
        description="Could not connect to the server. Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  const unlocked = data.filter((a) => a.unlocked_at);
  const unlockedCount = unlocked.length;
  const xpUnlocked = unlocked.reduce((sum, a) => sum + a.xp_reward, 0);
  const progress = data.length ? Math.round((unlockedCount / data.length) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 10 · Milestones &amp; badges
          </p>
          <h1 className="font-display text-3xl md:text-5xl font-medium tracking-tight leading-[1.08] text-ink mt-3">
            Milestone{" "}
            <span className="italic text-coral-600 dark:text-coral-400">Achievements.</span>
          </h1>
          <p className="text-ink-secondary mt-3">
            Proof-of-progress badges unlocked as you learn, practise, and ship.
          </p>
          <div className="mt-6">
            <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mb-1.5">
              <span>{unlockedCount} of {data.length} unlocked</span>
              <span className="tabular-nums">{progress}%</span>
            </div>
            <div className="h-1 rounded-full bg-surface-tertiary dark:bg-white/10 overflow-hidden" aria-hidden="true">
              <div className="h-full bg-coral-500" style={{ width: `${progress}%` }} />
            </div>
          </div>
        </div>
        <dl className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
          {[
            { label: "Unlocked", value: unlockedCount },
            { label: "Locked", value: data.length - unlockedCount },
            { label: "Total badges", value: data.length },
            { label: "XP from badges", value: xpUnlocked },
          ].map((stat) => (
            <div key={stat.label} className="bg-surface dark:bg-night-500 px-5 py-4">
              <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">{stat.label}</dt>
              <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{stat.value}</dd>
            </div>
          ))}
        </dl>
      </header>

      <div className="grid sm:grid-cols-2 gap-4">
        {data.map((ach) => {
          const isUnlocked = !!ach.unlocked_at;
          return (
            <Card
              key={ach.id}
              padding="md"
              className={cn(!isUnlocked && "opacity-60 grayscale")}
            >
              <div className="flex items-start gap-4">
                <div
                  className={cn(
                    "text-3xl h-12 w-12 rounded-lg flex items-center justify-center border shrink-0",
                    isUnlocked
                      ? "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20"
                      : "bg-surface-tertiary dark:bg-white/5 border-border dark:border-white/10",
                  )}
                  aria-hidden="true"
                >
                  {ach.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-display font-medium text-ink">{ach.name}</h3>
                    {isUnlocked ? (
                      <Star className="h-4 w-4 text-amber-500 fill-amber-500" aria-label="Unlocked" />
                    ) : (
                      <Lock className="h-3.5 w-3.5 text-ink-tertiary" aria-label="Locked" />
                    )}
                  </div>
                  <p className="text-sm text-ink-secondary mt-0.5">{ach.description}</p>
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    <Badge size="sm" variant="outline">
                      {categoryLabel[ach.category] || ach.category}
                    </Badge>
                    <span className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.1em] text-ink-tertiary">
                      <Zap className="h-3 w-3 text-amber-500" /> {ach.xp_reward} XP
                    </span>
                    {isUnlocked && ach.unlocked_at && (
                      <span className="font-mono text-[10px] uppercase tracking-[0.1em] text-ink-tertiary ml-auto">
                        {formatDate(ach.unlocked_at)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
