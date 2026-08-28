"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { courses as coursesApi, users as usersApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Rating } from "@/components/ui/ProgressBar";
import { PageLoader } from "@/components/ui/States";
import { formatDuration, formatNumber, difficultyColor, formatDate } from "@/lib/utils";
import {
  BookOpen, Clock, Users, Star, Award, Target, ChevronRight,
  Code2, Play, CheckCircle2, BarChart3, Globe, Layers, MessageSquare,
} from "lucide-react";
import toast from "react-hot-toast";
import type { Review } from "@/lib/types";

export default function CoursePage() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewText, setReviewText] = useState("");

  const { data: course, isLoading } = useQuery({
    queryKey: ["course", slug],
    queryFn: () => coursesApi.get(slug),
  });

  const { data: modules, isLoading: modulesLoading } = useQuery({
    queryKey: ["modules", slug],
    queryFn: () => coursesApi.getModules(slug),
  });

  const { data: reviews } = useQuery({
    queryKey: ["reviews", slug],
    queryFn: () => coursesApi.getReviews(slug),
  });

  const reviewMutation = useMutation({
    mutationFn: (data: { rating: number; review?: string }) => coursesApi.createReview(slug, data),
    onSuccess: () => {
      setReviewText("");
      queryClient.invalidateQueries({ queryKey: ["reviews", slug] });
      queryClient.invalidateQueries({ queryKey: ["course", slug] });
      toast.success("Review posted. Thank you!");
    },
    onError: (e: unknown) => {
      const apiErr = e as { detail?: string };
      toast.error(apiErr?.detail || "Could not post review.");
    },
  });

  const handleEnroll = async () => {
    if (!course) return;
    if (!isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(`/courses/${slug}`)}`);
      return;
    }
    try {
      await usersApi.enroll(course.id);
      toast.success("Enrolled successfully!");
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      if (apiErr.detail === "Already enrolled") {
        toast.error("You're already enrolled in this course");
      } else {
        toast.error("Failed to enroll. Please try again.");
      }
    }
  };

  if (isLoading) return <PageLoader />;
  if (!course) return <div className="text-center py-16">Course not found</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 md:p-12 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <p className="eyebrow mb-4 !text-coral-400">No. 03 — {course.language} curriculum</p>
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge size="sm" className="bg-coral-500/15 text-coral-400 dark:text-coral-400 border border-coral-500/30">
            {course.difficulty}
          </Badge>
          {course.skill_tags?.map((tag) => (
            <Badge key={tag} size="sm" variant="outline" className="bg-white/5 text-paper-50/70 dark:text-ink-secondary border-paper-50/15 dark:border-border">
              {tag}
            </Badge>
          ))}
        </div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight">{course.title}</h1>
        <p className="mt-3 text-paper-50/70 dark:text-ink-secondary text-lg max-w-2xl">{course.description}</p>

        <div className="flex flex-wrap items-center gap-6 mt-6 text-sm text-paper-50/60 dark:text-ink-tertiary">
          <span className="flex items-center gap-1.5">
            <BookOpen className="h-4 w-4" /> {course.lesson_count} lessons
          </span>
          {course.estimated_duration_minutes && (
            <span className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" /> {formatDuration(course.estimated_duration_minutes)}
            </span>
          )}
          <span className="flex items-center gap-1.5">
            <Users className="h-4 w-4" /> {formatNumber(course.enrollment_count)} enrolled
          </span>
          <span className="flex items-center gap-1.5">
            <Star className="h-4 w-4 text-amber-400 fill-amber-400" /> {course.rating_average} ({course.rating_count} reviews)
          </span>
        </div>

        <div className="mt-8">
          <Button
            size="lg"
            onClick={handleEnroll}
          >
            {isAuthenticated ? "Enroll Now" : "Start Learning"}
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-8">
          {/* What you'll learn */}
          {course.learning_objectives && (
            <section>
              <p className="eyebrow mb-2">Objectives</p>
              <h2 className="font-display text-xl font-semibold text-ink mb-4">What You&apos;ll Learn</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {course.learning_objectives.map((obj, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-ink-secondary">{obj}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Prerequisites */}
          {course.prerequisites && course.prerequisites.length > 0 && (
            <section>
              <p className="eyebrow mb-2">Before you start</p>
              <h2 className="font-display text-xl font-semibold text-ink mb-4">Prerequisites</h2>
              <div className="space-y-2">
                {course.prerequisites.map((pre, i) => (
                  <div key={i} className="flex items-center gap-2.5 text-sm text-ink-secondary">
                    <div className="h-1.5 w-1.5 rounded-full bg-ink-tertiary" />
                    {pre}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Course Content / Curriculum */}
          <section>
            <p className="eyebrow mb-2">Course content</p>
            <h2 className="font-display text-xl font-semibold text-ink mb-4">Course Curriculum</h2>
            {modules ? (
              <div className="space-y-3">
                {modules.map((mod, idx) => (
                  <div key={mod.id} className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 overflow-hidden hover:border-coral-400/50 transition-colors">
                    <div className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-4">
                        <span className="font-mono text-sm text-coral-600 dark:text-coral-400">
                          {String(idx + 1).padStart(2, "0")}
                        </span>
                        <div>
                          <h3 className="font-medium text-ink">{mod.title}</h3>
                          <p className="text-xs text-ink-tertiary mt-0.5">
                            {mod.lesson_count} lessons
                            {mod.estimated_duration_minutes && ` • ${formatDuration(mod.estimated_duration_minutes)}`}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-ink-tertiary" aria-hidden="true" />
                    </div>
                  </div>
                ))}
              </div>
            ) : modulesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-border p-4">
                    <div className="h-4 w-2/3 rounded bg-surface-tertiary dark:bg-white/5 animate-pulse" />
                    <div className="mt-2 h-3 w-1/3 rounded bg-surface-tertiary dark:bg-white/5 animate-pulse" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-ink-tertiary">Curriculum is not available right now.</div>
            )}
          </section>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card padding="md">
            <p className="eyebrow mb-2">At a glance</p>
            <h3 className="font-display text-lg font-semibold text-ink mb-3">Course Info</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Level</span>
                <Badge size="sm" className={difficultyColor(course.difficulty)}>
                  {course.difficulty}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Language</span>
                <span className="text-ink font-medium">{course.language}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Lessons</span>
                <span className="text-ink font-medium">{course.lesson_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Duration</span>
                <span className="text-ink font-medium">{formatDuration(course.estimated_duration_minutes)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Enrolled</span>
                <span className="text-ink font-medium">{formatNumber(course.enrollment_count)}</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-border">
              <Button className="w-full" size="lg" onClick={handleEnroll}>
                Enroll Now
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Reviews */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="eyebrow mb-2">Feedback</p>
            <h2 className="font-display text-xl font-semibold text-ink flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-coral-500" /> Student Reviews
            </h2>
          </div>
          {course.rating_count > 0 && <Rating value={course.rating_average} count={course.rating_count} size="md" />}
        </div>

        {/* Write review */}
        {isAuthenticated && (
          <Card padding="md" className="mb-4">
            <h3 className="font-display font-semibold text-ink mb-3">Write a review</h3>
            <div className="flex items-center gap-1 mb-3">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onClick={() => setReviewRating(n)}
                  aria-label={`${n} star${n > 1 ? "s" : ""}`}
                  className="p-0.5"
                >
                  <Star className={n <= reviewRating ? "h-6 w-6 fill-amber-400 text-amber-400" : "h-6 w-6 text-ink-tertiary"} />
                </button>
              ))}
            </div>
            <textarea
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              rows={3}
              placeholder="What did you think of this course?"
              className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 mb-3"
            />
            <div className="flex justify-end">
              <Button
                size="sm"
                loading={reviewMutation.isPending}
                onClick={() => reviewMutation.mutate({ rating: reviewRating, review: reviewText.trim() || undefined })}
              >
                Post Review
              </Button>
            </div>
          </Card>
        )}

        {reviews && reviews.items && reviews.items.length > 0 ? (
          <div className="space-y-3">
            {reviews.items.map((r: Review) => (
              <Card key={r.id} padding="md">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center text-coral-500 font-semibold text-xs">
                      {r.display_name?.[0]?.toUpperCase() || "U"}
                    </div>
                    <span className="text-sm font-medium text-ink">{r.display_name}</span>
                  </div>
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <Star key={n} className={n <= r.rating ? "h-4 w-4 fill-amber-400 text-amber-400" : "h-4 w-4 text-ink-tertiary"} />
                    ))}
                  </div>
                </div>
                {r.review && <p className="text-sm text-ink-secondary whitespace-pre-wrap">{r.review}</p>}
                <p className="text-xs text-ink-tertiary mt-2">{formatDate(r.created_at)}</p>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-sm text-ink-tertiary">No reviews yet. Be the first to review this course.</p>
        )}
      </section>
    </div>
  );
}
