"use client";

import { useQuery } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { Trophy, Star, Lock, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
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

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <p className="eyebrow mb-2">Milestones</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
          <Trophy className="h-8 w-8 text-amber-500 dark:text-amber-400" />
          Achievements
        </h1>
        <p className="text-ink-secondary mt-1">
          {unlockedCount}/{data.length} unlocked · earn XP as you learn
        </p>
      </div>

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
                    "text-3xl h-12 w-12 rounded-xl flex items-center justify-center border",
                    isUnlocked
                      ? "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20"
                      : "bg-surface-tertiary dark:bg-white/5 border-border dark:border-white/10",
                  )}
                  aria-hidden="true"
                >
                  {ach.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-display font-semibold text-ink">{ach.name}</h3>
                    {isUnlocked ? (
                      <Star className="h-4 w-4 text-amber-500 fill-amber-500" aria-label="Unlocked" />
                    ) : (
                      <Lock className="h-3.5 w-3.5 text-ink-tertiary" aria-label="Locked" />
                    )}
                  </div>
                  <p className="text-sm text-ink-secondary mt-0.5">{ach.description}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge size="sm" variant="outline">
                      {categoryLabel[ach.category] || ach.category}
                    </Badge>
                    <span className="flex items-center gap-1 text-xs text-ink-tertiary">
                      <Zap className="h-3 w-3 text-amber-400" /> {ach.xp_reward} XP
                    </span>
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
