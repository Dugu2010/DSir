"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { leaderboard } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { Trophy, Medal, Crown } from "lucide-react";
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
    if (rank === 1) return <Crown className="h-5 w-5 text-amber-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-slate-400" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-700 dark:text-amber-600" />;
    return <span className="text-sm font-mono text-ink-tertiary w-5 text-center tabular-nums">{rank}</span>;
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 11 · Community standings
          </p>
          <h1 className="font-display text-3xl md:text-5xl font-medium tracking-tight leading-[1.08] text-ink mt-3">
            Global{" "}
            <span className="italic text-coral-600 dark:text-coral-400">Leaderboard.</span>
          </h1>
          <p className="text-ink-secondary mt-3">Top learners by XP earned.</p>

          {/* Period tabs */}
          <div className="flex gap-1 p-1 mt-5 rounded-full border border-border dark:border-white/10 bg-surface-secondary dark:bg-white/[0.03] w-fit max-w-full overflow-x-auto">
            {periods.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                aria-pressed={period === p.value}
                className={cn(
                  "px-3.5 py-1.5 rounded-full text-[11px] font-mono uppercase tracking-[0.1em] whitespace-nowrap transition-colors",
                  period === p.value
                    ? "bg-coral-500 text-white"
                    : "text-ink-tertiary hover:text-ink",
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
        <dl className="grid grid-cols-3 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
          <div className="bg-surface dark:bg-night-500 px-5 py-4">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Your rank</dt>
            <dd className="font-display text-2xl font-medium text-coral-600 dark:text-coral-400 mt-1 tabular-nums">
              {myRank && myRank.rank > 0 ? `#${myRank.rank}` : "—"}
            </dd>
          </div>
          <div className="bg-surface dark:bg-night-500 px-5 py-4">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Your XP</dt>
            <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">
              {myRank ? formatNumber(myRank.xp_earned) : "0"}
            </dd>
          </div>
          <div className="bg-surface dark:bg-night-500 px-5 py-4">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Ranked</dt>
            <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{data.length}</dd>
          </div>
        </dl>
      </header>

      {data.length === 0 ? (
        <EmptyState
          title="No rankings yet"
          description="Be the first on the board — complete lessons and exercises to earn XP."
          icon={<Trophy className="h-8 w-8" />}
        />
      ) : (
        <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 divide-y divide-border dark:divide-white/10 overflow-hidden">
          {data.map((entry: LeaderboardEntry) => {
            const isMe = entry.user_id === user?.id;
            return (
              <div
                key={entry.user_id}
                className={cn(
                  "flex items-center gap-4 px-4 py-3.5",
                  isMe && "bg-coral-500/[0.06] dark:bg-coral-500/10",
                )}
              >
                <div className="w-8 flex justify-center">{rankIcon(entry.rank)}</div>
                <div className="h-9 w-9 rounded-md bg-coral-500/10 border border-coral-500/30 flex items-center justify-center text-coral-600 dark:text-coral-400 font-mono text-sm flex-shrink-0">
                  {entry.display_name?.[0]?.toUpperCase() || "?"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-ink truncate">
                    {entry.display_name}
                    {isMe && (
                      <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-coral-600 dark:text-coral-400 ml-2">(you)</span>
                    )}
                  </p>
                  <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-0.5">
                    Level {entry.current_level}
                  </p>
                </div>
                <p className="font-mono text-sm text-ink tabular-nums">{formatNumber(entry.xp_earned)} XP</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
