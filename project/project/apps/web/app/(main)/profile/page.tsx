"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Award, BookOpen, CheckCircle2, Flame, Trophy, Zap } from "lucide-react";
import { fetchMastery, fetchStrengthsWeaknesses, fetchUserAchievements, fetchUserStats } from "@/lib/api";
import { useAuthStore } from "@/hooks/use-auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/ui/stat-card";

export default function ProfilePage() {
  const { user } = useAuthStore();

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["user-stats"],
    queryFn: fetchUserStats,
  });

  const {
    data: achievementsData,
    isLoading: achievementsLoading,
    error: achievementsError,
  } = useQuery({
    queryKey: ["user-achievements"],
    queryFn: fetchUserAchievements,
  });

  const {
    data: mastery,
    isLoading: masteryLoading,
    error: masteryError,
    refetch: refetchMastery,
  } = useQuery({
    queryKey: ["mastery"],
    queryFn: fetchMastery,
  });

  const {
    data: strengthsWeaknesses,
    isLoading: swLoading,
    error: swError,
    refetch: refetchSw,
  } = useQuery({
    queryKey: ["strengths-weaknesses"],
    queryFn: fetchStrengthsWeaknesses,
  });

  const avgScore = useMemo(() => {
    if (!mastery?.items.length) return 0;
    return Math.round(mastery.items.reduce((acc, m) => acc + m.score, 0) / mastery.items.length);
  }, [mastery]);

  const isLoading = statsLoading || achievementsLoading || masteryLoading || swLoading;
  const error = statsError || achievementsError || masteryError || swError;

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
        <ErrorMessage>
          Failed to load profile data.{" "}
          <Button onClick={() => { refetchStats(); refetchMastery(); refetchSw(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  return (
    <div className="mx-auto max-w-6xl animate-fade-in space-y-8">
      <div className="flex items-start gap-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 text-3xl font-bold text-primary">
          {user?.full_name?.[0] ?? user?.email?.[0] ?? "U"}
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{user?.full_name ?? "Learner"}</h1>
          <p className="text-muted-foreground">{user?.email}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant="info">{stats?.xp ?? 0} XP</Badge>
            <Badge variant="warning">{stats?.current_streak ?? 0} day streak</Badge>
            <Badge variant="success">{stats?.lessons_completed ?? 0} lessons completed</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total XP"
          value={stats?.xp ?? 0}
          icon={<Zap className="h-5 w-5" />}
        />
        <StatCard
          label="Current Streak"
          value={`${stats?.current_streak ?? 0} days`}
          icon={<Flame className="h-5 w-5" />}
        />
        <StatCard
          label="Lessons Completed"
          value={stats?.lessons_completed ?? 0}
          icon={<CheckCircle2 className="h-5 w-5" />}
        />
        <StatCard
          label="Average Mastery"
          value={`${avgScore}%`}
          icon={<BookOpen className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <section className="lg:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <Trophy className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-bold">Achievements</h2>
          </div>
          {achievementsData?.items.length ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {achievementsData.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-start gap-4 rounded-2xl border border-border bg-card p-4 transition hover:shadow-sm"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Award className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{item.achievement.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.achievement.description}</p>
                    <p className="mt-1 text-xs font-medium text-primary">+{item.achievement.xp_reward} XP</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-8 text-center">
              <p className="text-muted-foreground">No achievements yet. Complete lessons to earn them!</p>
            </div>
          )}
        </section>

        <aside className="space-y-8">
          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-lg font-bold">Strengths</h2>
            {strengthsWeaknesses?.strengths.length ? (
              <ul className="mt-4 space-y-3">
                {strengthsWeaknesses.strengths.slice(0, 5).map((item) => (
                  <li key={item.concept_id} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{item.concept_id}</span>
                      <span className="text-muted-foreground">{item.score}%</span>
                    </div>
                    <Progress value={item.score} />
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">No strengths recorded yet.</p>
            )}
          </section>

          <section className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-lg font-bold">Areas to improve</h2>
            {strengthsWeaknesses?.weaknesses.length ? (
              <ul className="mt-4 space-y-3">
                {strengthsWeaknesses.weaknesses.slice(0, 5).map((item) => (
                  <li key={item.concept_id} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{item.concept_id}</span>
                      <span className="text-muted-foreground">{item.score}%</span>
                    </div>
                    <Progress value={item.score} barClassName="bg-amber-500" />
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">No weaknesses recorded yet. Great job!</p>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className="space-y-8">
      <div className="flex items-start gap-6">
        <Skeleton className="h-20 w-20 rounded-2xl" />
        <div className="space-y-3">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-2xl" />
        ))}
      </div>
      <Skeleton className="h-64 rounded-2xl" />
    </div>
  );
}
