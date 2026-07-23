"use client";

import { useMemo } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Award,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Flame,
  GraduationCap,
  LayoutDashboard,
  Play,
  RotateCcw,
  Sparkles,
  Zap,
} from "lucide-react";
import {
  continueCourse,
  fetchDueRevisions,
  fetchMyLearning,
  fetchRecentCourses,
  fetchRecommendations,
  fetchUserStats,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/ui/stat-card";
import { CourseCard } from "@/components/course-card";

export default function DashboardPage() {
  const router = useRouter();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["user-stats"],
    queryFn: fetchUserStats,
  });

  const {
    data: myLearning,
    isLoading: myLearningLoading,
    error: myLearningError,
  } = useQuery({
    queryKey: ["my-learning"],
    queryFn: fetchMyLearning,
  });

  const { data: recentCourses, isLoading: recentLoading } = useQuery({
    queryKey: ["recent-courses"],
    queryFn: fetchRecentCourses,
  });

  const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ["recommendations"],
    queryFn: fetchRecommendations,
  });

  const { data: dueRevisions, isLoading: dueLoading } = useQuery({
    queryKey: ["revision-due"],
    queryFn: fetchDueRevisions,
  });

  const continueMutation = useMutation({
    mutationFn: async (courseId: string) => {
      const result = await continueCourse(courseId);
      return { courseId, lessonId: result.lesson_id };
    },
    onSuccess: (data) => {
      if (data.lessonId) {
        router.push(`/learn/${data.courseId}/${data.lessonId}`);
      } else {
        router.push(`/courses/${data.courseId}`);
      }
    },
  });

  const isLoading = statsLoading || myLearningLoading || recentLoading || recommendationsLoading || dueLoading;
  const inProgress = useMemo(
    () => myLearning?.items.filter((item) => item.course && item.progress.progress_percent < 100) ?? [],
    [myLearning]
  );

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (myLearningError) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <ErrorMessage>Couldn&apos;t load your dashboard. Please try again.</ErrorMessage>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary to-indigo-600 px-6 py-10 text-white sm:px-10 sm:py-12">
        <div className="relative z-10 max-w-2xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-sm font-medium backdrop-blur-sm">
            <Sparkles className="h-4 w-4" />
            <span>Your learning command center</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Welcome back
          </h1>
          <p className="mt-3 max-w-lg text-lg text-white/90">
            Continue where you left off, track your streak, and discover your next challenge.
          </p>
          {inProgress.length > 0 && (
            <div className="mt-6">
              <Button
                onClick={() => continueMutation.mutate(inProgress[0].course!.id)}
                disabled={continueMutation.isPending}
                className="gap-2 bg-white text-primary hover:bg-white/90"
              >
                <Play className="h-4 w-4" />
                Continue {inProgress[0].course!.title}
              </Button>
            </div>
          )}
        </div>
        <div className="absolute right-6 top-1/2 hidden -translate-y-1/2 opacity-20 lg:block">
          <LayoutDashboard className="h-64 w-64" />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total XP"
          value={stats?.xp ?? 0}
          description="Keep learning to earn more"
          icon={<Zap className="h-5 w-5" />}
        />
        <StatCard
          label="Current Streak"
          value={`${stats?.current_streak ?? 0} days`}
          description="Daily learning builds momentum"
          icon={<Flame className="h-5 w-5" />}
        />
        <StatCard
          label="Lessons Completed"
          value={stats?.lessons_completed ?? 0}
          description="Total lessons finished"
          icon={<CheckCircle2 className="h-5 w-5" />}
        />
        <StatCard
          label="Courses Completed"
          value={stats?.courses_completed ?? 0}
          description="Certificates earned"
          icon={<Award className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Continue learning */}
        <section className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Continue learning</h2>
            <Link
              href="/courses"
              className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            >
              Browse courses <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          {inProgress.length > 0 ? (
            <div className="grid gap-4">
              {inProgress.map((item) => (
                <div
                  key={item.enrollment.id}
                  className="group relative overflow-hidden rounded-2xl border border-border bg-card p-5 transition hover:shadow-md"
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-start gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <BookOpen className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-card-foreground">{item.course!.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {item.progress.completed_lessons} / {item.progress.total_lessons} lessons
                        </p>
                        <div className="mt-2 w-full sm:w-64">
                          <Progress value={item.progress.progress_percent} />
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => continueMutation.mutate(item.course!.id)}
                      disabled={continueMutation.isPending}
                      className="gap-2"
                    >
                      <Play className="h-4 w-4" />
                      Resume
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-card/50 p-8 text-center">
              <GraduationCap className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold text-foreground">No active courses</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Enroll in a course to start tracking your progress.
              </p>
              <Link
                href="/courses"
                className="mt-4 inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
              >
                Explore courses
              </Link>
            </div>
          )}
        </section>

        {/* Side panel */}
        <aside className="space-y-8">
          {/* Weekly progress */}
          <section className="rounded-2xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-bold text-foreground">Weekly progress</h2>
            <p className="text-sm text-muted-foreground">Minutes learned this week</p>
            <div className="mt-6 flex items-end justify-between gap-2">
              {(stats?.weekly_minutes ?? []).map(([day, minutes], index) => {
                const height = Math.min((minutes / Math.max(stats?.daily_goal_minutes ?? 30, 1)) * 100, 100);
                const dayLabel = new Date(day).toLocaleDateString("en-US", { weekday: "narrow" });
                return (
                  <div key={index} className="flex flex-1 flex-col items-center gap-2">
                    <div className="relative w-full">
                      <div
                        className="w-full rounded-t-md bg-primary/20 transition-all"
                        style={{ height: `${Math.max(height, 4)}px` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground">{dayLabel}</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Revision reminders */}
          <section className="rounded-2xl border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <RotateCcw className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-bold text-foreground">Revision</h2>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              {dueRevisions && dueRevisions.length > 0 ? (
                <>
                  You have <strong>{dueRevisions.length}</strong> concepts due for review today.
                </>
              ) : (
                "No concepts due for review. Great job!"
              )}
            </p>
            <Link
              href="/revision"
              className="mt-4 inline-flex w-full items-center justify-center rounded-lg border border-border bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground transition hover:bg-secondary/80"
            >
              Start revision
            </Link>
          </section>
        </aside>
      </div>

      {/* Recently viewed */}
      {recentCourses && recentCourses.items.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Recently viewed</h2>
            <Link
              href="/courses/recently-viewed"
              className="text-sm font-medium text-primary hover:underline"
            >
              View all
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {recentCourses.items.slice(0, 4).map((item) => (
              <CourseCard key={item.course.id} course={item.course} />
            ))}
          </div>
        </section>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.items.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground">Recommended for you</h2>
            <Link
              href="/courses"
              className="text-sm font-medium text-primary hover:underline"
            >
              Explore
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {recommendations.items.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <Skeleton className="h-48 w-full rounded-3xl" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-2xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <Skeleton className="h-64 rounded-2xl lg:col-span-2" />
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    </div>
  );
}
