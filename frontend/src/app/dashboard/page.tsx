"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { users, learning } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { EmptyState, PageLoader, ErrorState } from "@/components/ui/States";
import { formatDuration, formatNumber, difficultyColor, levelProgress, xpForLevel } from "@/lib/utils";
import type { Dashboard, KnowledgeItem } from "@/lib/types";
import {
  BookOpen, Star, Clock, ArrowRight, ChevronRight, Flame, Target, Gauge, History,
} from "lucide-react";
import { useState } from "react";

function masteryLabel(value: number): string {
  if (value >= 85) return "Mastered";
  if (value >= 70) return "Advanced";
  if (value >= 50) return "Proficient";
  return "In Focus";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [goalEditorOpen, setGoalEditorOpen] = useState(false);
  const { data, isLoading, error, refetch } = useQuery<Dashboard>({
    queryKey: ["dashboard"],
    queryFn: () => users.getDashboard(),
  });

  const { data: knowledge } = useQuery<KnowledgeItem[]>({
    queryKey: ["knowledge"],
    queryFn: () => users.getKnowledge(),
  });

  const { data: recentlyViewed } = useQuery({
    queryKey: ["recently-viewed"],
    queryFn: () => learning.getRecentlyViewed(),
  });

  const updateGoal = useMutation({
    mutationFn: users.updateDailyGoal,
    onSuccess: async () => {
      setGoalEditorOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (isLoading) return <PageLoader />;
  if (error || !data) {
    return (
      <ErrorState
        title="Failed to load dashboard"
        description="Could not connect to the server. Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  const { stats } = data;
  const progress = levelProgress(stats.total_xp, stats.current_level);
  const firstName = user?.display_name?.split(" ")[0];
  const resumeHref = data.continue_learning.length > 0
    ? `/courses/${data.continue_learning[0].course.slug}/learn`
    : "/courses";

  const cockpitStats = [
    { label: "Persistence", value: `${stats.current_streak}`, suffix: "days" },
    { label: "Level", value: `L${stats.current_level}`, suffix: `${formatNumber(stats.total_xp)} XP` },
    { label: "Lessons", value: formatNumber(stats.lessons_completed), suffix: "completed" },
    { label: "Exercises", value: formatNumber(stats.exercises_completed), suffix: "solved" },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-10">
      {/* Cockpit hero */}
      <section className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="grid lg:grid-cols-12">
          <div className="lg:col-span-7 p-6 md:p-10">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-4">
              — No. 01 — Learner cockpit
            </p>
            <h1 className="font-display text-3xl md:text-4xl font-medium tracking-tight leading-[1.1] text-ink">
              Welcome back,{" "}
              <span className="italic text-coral-600 dark:text-coral-400">{firstName}.</span>
            </h1>
            <p className="mt-3 text-ink-secondary leading-relaxed max-w-md">
              Pick up where you left off — your next lesson is one keystroke away.
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-6">
              <Link href={resumeHref}>
                <Button size="lg" rightIcon={<ArrowRight className="h-4 w-4" />}>
                  Resume Learning
                </Button>
              </Link>
              <Link href="/courses">
                <Button size="lg" variant="outline">
                  Browse Catalog
                </Button>
              </Link>
            </div>
          </div>

          <div className="lg:col-span-5 border-t lg:border-t-0 lg:border-l border-border dark:border-white/10 grid grid-cols-2 gap-px bg-border dark:bg-white/10">
            {cockpitStats.map((s) => (
              <div key={s.label} className="bg-surface dark:bg-night-500 p-5 md:p-6">
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary">{s.label}</p>
                <p className="mt-2 font-display text-3xl font-medium text-ink leading-none">
                  {s.value}
                </p>
                <p className="mt-1.5 font-mono text-[10px] uppercase tracking-wide text-ink-tertiary flex items-center gap-1">
                  {s.label === "Persistence" && <Flame className="h-3 w-3 text-coral-500" aria-hidden="true" />}
                  {s.suffix}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Level progress strip */}
        <div className="border-t border-border dark:border-white/10 px-6 md:px-10 py-4 flex items-center gap-4">
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary flex-shrink-0">
            Level {stats.current_level}
          </span>
          <div className="flex-1 h-1.5 rounded-full bg-surface-tertiary dark:bg-white/10 overflow-hidden">
            <div
              className="h-full rounded-full bg-coral-500 transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary flex-shrink-0">
            {formatNumber(stats.total_xp)} / {xpForLevel(stats.current_level + 1)} XP
          </span>
        </div>
      </section>

      {/* Daily Goal */}
      <section>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Daily protocol</p>
        <div className="flex items-end justify-between gap-3 mb-4">
          <h2 className="font-display text-2xl font-medium tracking-tight text-ink flex items-center gap-2">
            <Target className="h-5 w-5 text-coral-500" aria-hidden="true" /> Daily Goal
          </h2>
          <div className="flex items-center gap-3">
            {data.daily_goal?.is_completed && <Badge variant="success">Completed</Badge>}
            <Button type="button" variant="outline" size="sm" onClick={() => setGoalEditorOpen((open) => !open)}>
              {goalEditorOpen ? "Cancel" : "Edit goal"}
            </Button>
          </div>
        </div>
        <Card padding="md">
          <div className="grid grid-cols-3 gap-px bg-border dark:bg-white/10 rounded-lg overflow-hidden">
            {[
              { label: "Minutes", actual: data.daily_goal?.actual_minutes ?? 0, target: data.daily_goal?.target_minutes ?? 30 },
              { label: "Lessons", actual: data.daily_goal?.actual_lessons ?? 0, target: data.daily_goal?.target_lessons ?? 1 },
              { label: "Exercises", actual: data.daily_goal?.actual_exercises ?? 0, target: data.daily_goal?.target_exercises ?? 2 },
            ].map((m) => (
              <div key={m.label} className="bg-surface dark:bg-night-500 p-4 text-center">
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary">{m.label}</p>
                <p className="mt-2 font-display text-xl font-medium text-ink">
                  {m.actual}<span className="text-ink-tertiary text-sm"> / {m.target}</span>
                </p>
              </div>
            ))}
          </div>

          {goalEditorOpen && (
            <form
              className="mt-5 border-t border-border dark:border-white/10 pt-4"
              onSubmit={(event) => {
                event.preventDefault();
                const values = new FormData(event.currentTarget);
                updateGoal.mutate({
                  target_minutes: Number(values.get("target_minutes")),
                  target_lessons: Number(values.get("target_lessons")),
                  target_exercises: Number(values.get("target_exercises")),
                });
              }}
            >
              <div className="grid sm:grid-cols-3 gap-4">
                <label className="text-sm font-medium text-ink">
                  Minutes
                  <input name="target_minutes" type="number" min={5} max={480} required defaultValue={data.daily_goal?.target_minutes ?? 30}
                    className="mt-1 block w-full rounded-lg border border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600 px-3 py-2 text-ink" />
                </label>
                <label className="text-sm font-medium text-ink">
                  Lessons
                  <input name="target_lessons" type="number" min={1} max={50} required defaultValue={data.daily_goal?.target_lessons ?? 1}
                    className="mt-1 block w-full rounded-lg border border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600 px-3 py-2 text-ink" />
                </label>
                <label className="text-sm font-medium text-ink">
                  Exercises
                  <input name="target_exercises" type="number" min={1} max={100} required defaultValue={data.daily_goal?.target_exercises ?? 2}
                    className="mt-1 block w-full rounded-lg border border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600 px-3 py-2 text-ink" />
                </label>
              </div>
              {updateGoal.isError && <p role="alert" className="mt-3 text-sm text-red-600">Could not update your goal. Please try again.</p>}
              <div className="mt-4 flex justify-end">
                <Button type="submit" size="sm" loading={updateGoal.isPending}>Save goal</Button>
              </div>
            </form>
          )}
        </Card>
      </section>

      {/* Continue Learning */}
      <section>
        <div className="flex items-end justify-between gap-3 mb-4">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Curriculum in motion</p>
            <h2 className="font-display text-2xl font-medium tracking-tight text-ink">Continue Learning</h2>
          </div>
          <Link href="/courses" className="font-mono text-[11px] uppercase tracking-wide text-coral-600 dark:text-coral-400 hover:underline flex items-center gap-1 flex-shrink-0">
            Browse all <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
          </Link>
        </div>

        {data.continue_learning.length === 0 ? (
          <EmptyState
            title="Start your first course"
            description="Browse our course catalog and begin your learning journey."
            icon={<BookOpen className="h-8 w-8" />}
            action={
              <Link href="/courses">
                <Button>Browse Courses</Button>
              </Link>
            }
          />
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.continue_learning.map((enrollment) => (
              <Link key={enrollment.id} href={`/courses/${enrollment.course.slug}/learn`}>
                <Card hover padding="md" className="h-full">
                  <div className="flex items-start justify-between mb-3">
                    <Badge size="sm" className={difficultyColor(enrollment.course.difficulty)}>
                      {enrollment.course.difficulty}
                    </Badge>
                    <span className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary">
                      {Math.round(enrollment.progress_percentage)}% complete
                    </span>
                  </div>
                  <h3 className="font-display text-lg font-medium text-ink mb-1 line-clamp-2 leading-snug">{enrollment.course.title}</h3>
                  <p className="text-sm text-ink-secondary line-clamp-2 mb-4">{enrollment.course.description}</p>
                  <div className="h-1 rounded-full bg-surface-tertiary dark:bg-white/10 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-coral-500 transition-all"
                      style={{ width: `${enrollment.progress_percentage}%` }}
                    />
                  </div>
                  <div className="flex items-center gap-3 mt-3 font-mono text-[10px] uppercase tracking-wide text-ink-tertiary">
                    <span className="flex items-center gap-1">
                      <BookOpen className="h-3 w-3" aria-hidden="true" />
                      {enrollment.course.lesson_count} lessons
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" aria-hidden="true" />
                      {formatDuration(enrollment.course.estimated_duration_minutes)}
                    </span>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Recommended Courses */}
      <section>
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Recommended tracks</p>
        <h2 className="font-display text-2xl font-medium tracking-tight text-ink mb-4">Recommended For You</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.recommended_courses.slice(0, 6).map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`}>
              <Card hover padding="md" className="h-full">
                <div className="flex items-start justify-between mb-3">
                  <Badge size="sm" className={difficultyColor(course.difficulty)}>
                    {course.difficulty}
                  </Badge>
                  <div className="flex items-center gap-1 text-amber-500">
                    <Star className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                    <span className="font-mono text-[10px] text-ink-secondary">{course.rating_average}</span>
                  </div>
                </div>
                <h3 className="font-display text-lg font-medium text-ink mb-1 line-clamp-2 leading-snug">{course.title}</h3>
                <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{course.description}</p>
                {course.skill_tags && (
                  <div className="flex flex-wrap gap-1.5">
                    {course.skill_tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} size="sm" variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Recently Viewed */}
      {recentlyViewed && recentlyViewed.length > 0 && (
        <section>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Recent sessions</p>
          <h2 className="font-display text-2xl font-medium tracking-tight text-ink flex items-center gap-2 mb-4">
            <History className="h-5 w-5 text-coral-500" aria-hidden="true" /> Recently Viewed
          </h2>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {recentlyViewed.slice(0, 6).map((item: any) => (
              <Link
                key={item.lesson_id}
                href={`/courses/${item.course_slug}/learn/${item.module_slug}/${item.lesson_slug}`}
                className="flex-shrink-0 w-64 rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-4 hover:border-coral-500/40 transition-colors"
              >
                <p className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary mb-1.5 truncate">{item.course_title}</p>
                <p className="text-sm font-medium text-ink line-clamp-2">{item.lesson_title}</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* My Skills / Mastery */}
      {knowledge && knowledge.length > 0 && (
        <section>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Telemetry overview</p>
          <h2 className="font-display text-2xl font-medium tracking-tight text-ink flex items-center gap-2 mb-4">
            <Gauge className="h-5 w-5 text-coral-500" aria-hidden="true" /> Skill Diagnostic Matrix
          </h2>
          <Card padding="md">
            <div className="grid sm:grid-cols-2 gap-x-8 gap-y-5">
              {knowledge.slice(0, 8).map((k) => (
                <div key={k.slug}>
                  <div className="flex items-center justify-between mb-1.5 gap-3">
                    <span className="text-sm font-medium text-ink capitalize truncate">{k.topic}</span>
                    <span className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary flex-shrink-0">
                      {Math.round(k.mastery_level)}% · {masteryLabel(k.mastery_level)}
                    </span>
                  </div>
                  <ProgressBar value={k.mastery_level} showLabel={false} size="sm" />
                </div>
              ))}
            </div>
          </Card>
        </section>
      )}

      {/* Achievements */}
      {data.achievements.length > 0 && (
        <section>
          <div className="flex items-end justify-between gap-3 mb-4">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Honors</p>
              <h2 className="font-display text-2xl font-medium tracking-tight text-ink">Recent Achievements</h2>
            </div>
            <Link href="/achievements" className="font-mono text-[11px] uppercase tracking-wide text-coral-600 dark:text-coral-400 hover:underline flex-shrink-0">
              View all
            </Link>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {data.achievements.map((ach) => (
              <div
                key={ach.id}
                className="flex-shrink-0 w-40 rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-4 text-center hover:border-coral-500/40 transition-colors"
              >
                <div className="text-3xl mb-2">{ach.icon}</div>
                <p className="text-sm font-medium text-ink line-clamp-1">{ach.name}</p>
                <p className="text-xs text-ink-tertiary mt-1 line-clamp-2">{ach.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
