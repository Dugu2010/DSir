"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import {
  BookOpen,
  Bookmark,
  CheckCircle2,
  ChevronDown,
  Clock,
  GraduationCap,
  Play,
  Sparkles,
  Target,
  User,
} from "lucide-react";
import { createBookmark, createEnrollment, deleteBookmark, fetchBookmarks, fetchCourseDetail } from "@/lib/api";
import { useAuthStore } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Skeleton } from "@/components/ui/skeleton";

function formatDuration(minutes: number) {
  if (minutes < 60) return `${minutes} min`;
  return `${Math.round(minutes / 60)}h`;
}

function formatDifficulty(difficulty: string) {
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
}

export default function CourseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["course-detail", id],
    queryFn: () => fetchCourseDetail(id),
  });

  const { data: bookmarksData } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: fetchBookmarks,
    enabled: isAuthenticated,
  });

  const existingBookmark = bookmarksData?.items.find((b) => b.course_id === id);

  const enrollMutation = useMutation({
    mutationFn: () => createEnrollment({ course_id: id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course-detail", id] });
      queryClient.invalidateQueries({ queryKey: ["my-learning"] });
      queryClient.invalidateQueries({ queryKey: ["enrollments"] });
    },
  });

  const bookmarkMutation = useMutation({
    mutationFn: async () => {
      if (existingBookmark) {
        await deleteBookmark(existingBookmark.id);
      } else {
        await createBookmark(id);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
    },
  });

  const toggleModule = (moduleId: string) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) {
        next.delete(moduleId);
      } else {
        next.add(moduleId);
      }
      return next;
    });
  };

  if (isLoading) {
    return <CourseDetailSkeleton />;
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <ErrorMessage>
          Failed to load course details.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  const { course, modules, enrollment, progress } = data;
  const firstIncompleteLesson = modules
    .flatMap((m) => m.lessons)
    .find((lesson) => !lesson.is_completed);
  const continueLessonId = firstIncompleteLesson?.id ?? modules[0]?.lessons[0]?.id;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 to-slate-800 px-6 py-12 text-white sm:px-12 sm:py-16">
        <div className="relative z-10 grid gap-8 lg:grid-cols-2 lg:items-center">
          <div className="space-y-6">
            <div className="flex flex-wrap gap-2">
              <span className="rounded-full bg-blue-500/20 px-3 py-1 text-sm font-medium text-blue-200">
                {course.category}
              </span>
              <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-sm font-medium text-emerald-200">
                {course.programming_language}
              </span>
              <span className="rounded-full bg-amber-500/20 px-3 py-1 text-sm font-medium text-amber-200">
                {formatDifficulty(course.difficulty)}
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              {course.title}
            </h1>
            <p className="max-w-xl text-lg text-slate-300">{course.description}</p>

            <div className="flex flex-wrap items-center gap-6 text-sm text-slate-300">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>{formatDuration(course.estimated_duration)}</span>
              </div>
              <div className="flex items-center gap-2">
                <GraduationCap className="h-4 w-4" />
                <span>{modules.length} modules</span>
              </div>
              <div className="flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                <span>{modules.flatMap((m) => m.lessons).length} lessons</span>
              </div>
              {course.instructor && (
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span>{course.instructor}</span>
                </div>
              )}
            </div>

            <div className="flex flex-wrap gap-3">
              {enrollment ? (
                <Link
                  href={`/learn/${course.id}/${continueLessonId}`}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
                >
                  <Play className="h-5 w-5" />
                  {progress.progress_percent > 0 ? "Continue Learning" : "Start Learning"}
                </Link>
              ) : isAuthenticated ? (
                <Button
                  onClick={() => enrollMutation.mutate()}
                  disabled={enrollMutation.isPending}
                  size="lg"
                  className="gap-2"
                >
                  {enrollMutation.isPending ? "Enrolling..." : "Enroll Now"}
                </Button>
              ) : (
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
                >
                  Sign in to Enroll
                </Link>
              )}
              {isAuthenticated && (
                <Button
                  onClick={() => bookmarkMutation.mutate()}
                  disabled={bookmarkMutation.isPending}
                  variant="secondary"
                  size="lg"
                  className="gap-2"
                >
                  <Bookmark className={`h-5 w-5 ${existingBookmark ? "fill-current" : ""}`} />
                  {existingBookmark ? "Bookmarked" : "Bookmark"}
                </Button>
              )}
            </div>
            {progress.progress_percent > 0 && (
              <div className="flex w-fit items-center gap-3 rounded-xl border border-white/20 bg-white/10 px-4 py-2 backdrop-blur-sm">
                <div className="h-2 w-32 overflow-hidden rounded-full bg-white/20">
                  <div
                    className="h-full rounded-full bg-blue-500 transition-all"
                    style={{ width: `${progress.progress_percent}%` }}
                  />
                </div>
                <span className="text-sm font-medium">{progress.progress_percent}% complete</span>
              </div>
            )}
          </div>

          <div className="relative hidden aspect-video overflow-hidden rounded-2xl lg:block">
            <Image
              src={course.thumbnail ?? "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop"}
              alt={course.title}
              fill
              sizes="(max-width: 1024px) 100vw, 50vw"
              className="object-cover"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Main content */}
        <div className="space-y-8 lg:col-span-2">
          {/* Skills */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Skills you&apos;ll learn</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {course.skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                >
                  {skill}
                </span>
              ))}
            </div>
          </section>

          {/* Learning objectives */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Learning objectives</h2>
            <ul className="mt-4 space-y-3">
              {course.learning_objectives.map((objective, index) => (
                <li key={index} className="flex items-start gap-3">
                  <Target className="mt-0.5 h-5 w-5 shrink-0 text-blue-600 dark:text-blue-400" />
                  <span className="text-slate-700 dark:text-slate-300">{objective}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Curriculum */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Course curriculum</h2>
            <div className="mt-4 space-y-3">
              {modules.map((module) => (
                <div
                  key={module.id}
                  className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700"
                >
                  <button
                    onClick={() => toggleModule(module.id)}
                    className="flex w-full items-center justify-between p-4 text-left transition hover:bg-slate-50 dark:hover:bg-slate-800"
                  >
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">{module.title}</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {module.lessons.length} lessons
                      </p>
                    </div>
                    <ChevronDown
                      className={`h-5 w-5 text-slate-500 transition-transform ${
                        expandedModules.has(module.id) ? "rotate-180" : ""
                      }`}
                    />
                  </button>
                  {expandedModules.has(module.id) && (
                    <ul className="divide-y divide-slate-100 dark:divide-slate-800">
                      {module.lessons.map((lesson, index) => (
                        <li
                          key={lesson.id}
                          className="flex items-center justify-between p-4 text-sm text-slate-700 dark:text-slate-300"
                        >
                          <div className="flex items-center gap-3">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-xs font-medium dark:bg-slate-800">
                              {index + 1}
                            </span>
                            <span>{lesson.title}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            {lesson.is_completed && (
                              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                            )}
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                              {lesson.duration_minutes} min
                            </span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Course progress</h2>
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">Completed</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {progress.completed_lessons} / {progress.total_lessons} lessons
                </span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                <div
                  className="h-full rounded-full bg-blue-600 transition-all"
                  style={{ width: `${progress.progress_percent}%` }}
                />
              </div>
              <p className="mt-2 text-sm font-medium text-slate-900 dark:text-white">
                {progress.progress_percent}% complete
              </p>
            </div>
            {!enrollment &&
              (isAuthenticated ? (
                <Button
                  onClick={() => enrollMutation.mutate()}
                  disabled={enrollMutation.isPending}
                  className="mt-6 w-full"
                >
                  {enrollMutation.isPending ? "Enrolling..." : "Enroll Now"}
                </Button>
              ) : (
                <Link
                  href="/login"
                  className="mt-6 flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  Sign in to Enroll
                </Link>
              ))}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-gradient-to-br from-blue-50 to-violet-50 p-6 dark:border-slate-700 dark:from-slate-900 dark:to-slate-900">
            <div className="flex items-start gap-3">
              <Sparkles className="mt-1 h-6 w-6 text-blue-600 dark:text-blue-400" />
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">AI-powered learning</h3>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                  Get personalized help, code reviews, and explanations from your AI mentor as you learn.
                </p>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

function CourseDetailSkeleton() {
  return (
    <div className="space-y-8">
      <div className="rounded-3xl bg-slate-200 px-6 py-12 dark:bg-slate-800 sm:px-12 sm:py-16">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="space-y-4">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-10 w-40" />
          </div>
          <Skeleton className="hidden aspect-video lg:block" />
        </div>
      </div>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-8 lg:col-span-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}
