"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { users } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton, CardSkeleton } from "@/components/ui/Skeleton";
import { EmptyState, PageLoader } from "@/components/ui/States";
import { formatDuration, formatNumber, difficultyColor, levelProgress, xpForLevel } from "@/lib/utils";
import type { Dashboard } from "@/lib/types";
import {
  BookOpen, Code2, Brain, Sparkles, TrendingUp,
  Flame, Target, Trophy, Star, Clock, ArrowRight,
  Play, ChevronRight, Zap, Award, CalendarDays,
} from "lucide-react";
import { useState } from "react";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery<Dashboard>({
    queryKey: ["dashboard"],
    queryFn: () => users.getDashboard(),
  });

  if (isLoading) return <PageLoader />;
  if (!data) return <EmptyState title="Failed to load dashboard" />;

  const { stats } = data;
  const progress = levelProgress(stats.total_xp, stats.current_level);

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome & Stats */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Greeting */}
        <div className="flex-1 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-800 p-8 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <h1 className="text-2xl font-bold">
              Welcome back, {user?.display_name?.split(" ")[0]}!
            </h1>
            <p className="text-white/80 mt-1">Continue your learning journey.</p>
            <div className="flex items-center gap-4 mt-6">
              <div className="flex items-center gap-2">
                <Flame className="h-5 w-5 text-orange-300" />
                <span className="font-semibold">{stats.current_streak} day streak</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-300" />
                <span className="font-semibold">{formatNumber(stats.total_xp)} XP</span>
              </div>
            </div>
          </div>
        </div>

        {/* XP Card */}
        <Card className="w-full lg:w-80">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-ink-secondary">Level {stats.current_level}</span>
            <span className="text-xs text-ink-tertiary">
              {stats.total_xp} / {xpForLevel(stats.current_level + 1)} XP
            </span>
          </div>
          <div className="h-3 rounded-full bg-surface-secondary overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-600 transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between mt-4 text-sm">
            <div className="flex items-center gap-1.5 text-ink-secondary">
              <BookOpen className="h-4 w-4" />
              {stats.lessons_completed} lessons
            </div>
            <div className="flex items-center gap-1.5 text-ink-secondary">
              <Code2 className="h-4 w-4" />
              {stats.exercises_completed} exercises
            </div>
          </div>
        </Card>
      </div>

      {/* Daily Goal */}
      {data.daily_goal && (
        <Card padding="md" className="border-brand-200 dark:border-brand-900 bg-brand-50/50 dark:bg-brand-950/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Target className="h-5 w-5 text-brand-600" />
              <div>
                <h3 className="font-semibold text-ink">Daily Goal</h3>
                <p className="text-sm text-ink-secondary">
                  {data.daily_goal.actual_minutes}/{data.daily_goal.target_minutes} min •
                  {data.daily_goal.actual_lessons}/{data.daily_goal.target_lessons} lessons •
                  {data.daily_goal.actual_exercises}/{data.daily_goal.target_exercises} exercises
                </p>
              </div>
            </div>
            {data.daily_goal.is_completed && <Badge variant="success">Completed!</Badge>}
          </div>
        </Card>
      )}

      {/* Continue Learning */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-ink">Continue Learning</h2>
          <Link href="/courses" className="text-sm text-brand-600 hover:underline font-medium flex items-center gap-1">
            Browse all courses <ChevronRight className="h-4 w-4" />
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
                <Card hover padding="md">
                  <div className="flex items-start justify-between mb-3">
                    <Badge size="sm" className={difficultyColor(enrollment.course.difficulty)}>
                      {enrollment.course.difficulty}
                    </Badge>
                    <span className="text-xs text-ink-tertiary">
                      {Math.round(enrollment.progress_percentage)}%
                    </span>
                  </div>
                  <h3 className="font-semibold text-ink mb-1 line-clamp-2">{enrollment.course.title}</h3>
                  <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{enrollment.course.description}</p>
                  <div className="h-1.5 rounded-full bg-surface-secondary overflow-hidden">
                    <div
                      className="h-full rounded-full bg-brand-500 transition-all"
                      style={{ width: `${enrollment.progress_percentage}%` }}
                    />
                  </div>
                  <div className="flex items-center gap-3 mt-3 text-xs text-ink-tertiary">
                    <span className="flex items-center gap-1">
                      <BookOpen className="h-3 w-3" />
                      {enrollment.course.lesson_count} lessons
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
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
        <h2 className="text-xl font-bold text-ink mb-4">Recommended For You</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.recommended_courses.slice(0, 6).map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`}>
              <Card hover padding="md">
                <div className="flex items-start justify-between mb-3">
                  <Badge size="sm" className={difficultyColor(course.difficulty)}>
                    {course.difficulty}
                  </Badge>
                  <div className="flex items-center gap-1 text-amber-500">
                    <Star className="h-3.5 w-3.5 fill-current" />
                    <span className="text-xs font-medium text-ink-secondary">{course.rating_average}</span>
                  </div>
                </div>
                <h3 className="font-semibold text-ink mb-1 line-clamp-2">{course.title}</h3>
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

      {/* Achievements */}
      {data.achievements.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-ink">Recent Achievements</h2>
            <Link href="/achievements" className="text-sm text-brand-600 hover:underline font-medium">
              View all
            </Link>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {data.achievements.map((ach) => (
              <div
                key={ach.id}
                className="flex-shrink-0 w-40 rounded-2xl border border-border p-4 text-center hover:shadow-md transition-shadow"
              >
                <div className="text-3xl mb-2">{ach.icon}</div>
                <p className="text-sm font-medium text-ink">{ach.name}</p>
                <p className="text-xs text-ink-tertiary mt-1">{ach.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
