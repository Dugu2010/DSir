"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { leaderboard } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { BarChart3, Trophy, Medal, Crown } from "lucide-react";
import { cn, formatNumber } from "@/lib/utils";
import type { LeaderboardEntry } from "@/lib/types";

const periods = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "all_time", label: "All Time" },
] as const;

export default function LeaderboardPage() {
  const { user } = useAuth();
  const [period, setPeriod] = useState<"daily" | "weekly" | "monthly" | "all_time">("weekly");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["leaderboard", period],
    queryFn: () => leaderboard.get(period),
  });
  const { data: myRank } = useQuery({
    queryKey: ["my-rank", period],
    queryFn: () => leaderboard.getMyRank(period),
  });

  if (isLoading) return <PageLoader label="Loading leaderboard..." />;
  if (error || !data) {
    return (
      <ErrorState
        title="Couldn't load leaderboard"
        description="Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  const rankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="h-5 w-5 text-amber-400" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-slate-400" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />;
    return <span className="text-sm font-mono text-ink-tertiary w-5 text-center">{rank}</span>;
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <p className="eyebrow mb-2">Community</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
          <BarChart3 className="h-8 w-8 text-coral-500" />
          Leaderboard
        </h1>
        <p className="text-ink-secondary mt-1">Top learners by XP earned.</p>
      </div>

      {/* Period tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-surface-tertiary dark:bg-white/5 w-fit">
        {periods.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            className={cn(
              "px-4 py-1.5 rounded-lg text-sm font-medium transition-colors",
              period === p.value
                ? "bg-surface dark:bg-night-500 text-ink shadow-sm"
                : "text-ink-tertiary hover:text-ink",
            )}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* My rank */}
      {myRank && myRank.rank > 0 && (
        <Card padding="sm" className="bg-coral-50/60 dark:bg-coral-500/5 border-coral-200 dark:border-coral-500/10 flex items-center gap-3">
          <Trophy className="h-5 w-5 text-coral-500" />
          <p className="text-sm text-ink">
            Your rank: <span className="font-semibold text-coral-600 dark:text-coral-400">#{myRank.rank}</span>
            {" "}· {formatNumber(myRank.xp_earned)} XP this period
          </p>
        </Card>
      )}

      {data.length === 0 ? (
        <EmptyState
          title="No rankings yet"
          description="Be the first on the board — complete lessons and exercises to earn XP."
          icon={<Trophy className="h-8 w-8" />}
        />
      ) : (
        <div className="space-y-2">
          {data.map((entry: LeaderboardEntry) => {
            const isMe = entry.user_id === user?.id;
            return (
              <div
                key={entry.user_id}
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-2xl border",
                  isMe
                    ? "border-coral-300 dark:border-coral-500/40 bg-coral-50/60 dark:bg-coral-500/10"
                    : "border-border dark:border-white/10 bg-surface dark:bg-night-500",
                )}
              >
                <div className="w-8 flex justify-center">{rankIcon(entry.rank)}</div>
                <div className="h-10 w-10 rounded-full bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center text-coral-500 font-semibold text-sm flex-shrink-0">
                  {entry.display_name?.[0]?.toUpperCase() || "?"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">
                    {entry.display_name}
                    {isMe && <span className="text-xs text-coral-500 ml-2">(you)</span>}
                  </p>
                  <p className="text-xs text-ink-tertiary">Level {entry.current_level}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-ink">{formatNumber(entry.xp_earned)} XP</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
