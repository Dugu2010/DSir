"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { courses as coursesApi, users as usersApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Rating } from "@/components/ui/ProgressBar";
import { PageLoader } from "@/components/ui/States";
import { formatDuration, formatNumber, difficultyColor, formatDate } from "@/lib/utils";
import {
  Star, ChevronRight, ArrowRight, CheckCircle2, MessageSquare,
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

  const titleWords = course.title.trim().split(/\s+/);
  const titleHead = titleWords.length > 1 ? titleWords.slice(0, -1).join(" ") : course.title;
  const titleLast = titleWords.length > 1 ? titleWords[titleWords.length - 1] : "";

  const specs = [
    { label: "Lessons", value: String(course.lesson_count) },
    { label: "Duration", value: course.estimated_duration_minutes ? formatDuration(course.estimated_duration_minutes) : "—" },
    { label: "Engineers", value: formatNumber(course.enrollment_count) },
    { label: "Rating", value: course.rating_count > 0 ? `${course.rating_average.toFixed(1)} (${course.rating_count})` : "—" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-10">
      {/* Hero */}
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-10">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-4">
            {"// "}No. 03 · {course.language} curriculum
          </p>
          <div className="flex flex-wrap gap-2 mb-5">
            <Badge size="sm" className={difficultyColor(course.difficulty)}>
              {course.difficulty}
            </Badge>
            {course.skill_tags?.map((tag) => (
              <Badge key={tag} size="sm" variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
          <h1 className="font-display text-3xl md:text-5xl font-medium tracking-tight leading-[1.08] text-ink max-w-3xl">
            {titleHead}{" "}
            {titleLast && <span className="italic text-coral-600 dark:text-coral-400">{titleLast}</span>}
          </h1>
          <p className="mt-4 text-ink-secondary text-base md:text-lg leading-relaxed max-w-2xl">{course.description}</p>

          {/* Spec strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-4 mt-8 pt-6 border-t border-border dark:border-white/10">
            {specs.map((s) => (
              <div key={s.label}>
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary">{s.label}</p>
                <p className="mt-1.5 font-display text-lg font-medium text-ink">{s.value}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-8">
            <Button size="lg" onClick={handleEnroll} rightIcon={<ArrowRight className="h-4 w-4" />}>
              {isAuthenticated ? "Enroll Now" : "Start Learning"}
            </Button>
            <a
              href="#curriculum"
              className="inline-flex items-center justify-center h-11 px-5 rounded-full border border-border text-sm font-medium text-ink hover:bg-surface-tertiary transition-colors"
            >
              Preview Curriculum
            </a>
          </div>
        </div>
      </header>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-10">
          {/* What you'll learn */}
          {course.learning_objectives && (
            <section>
              <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Objectives</p>
              <h2 className="font-display text-2xl font-medium tracking-tight text-ink mb-4">What You&apos;ll Master</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {course.learning_objectives.map((obj, i) => (
                  <div key={i} className="flex items-start gap-2.5 rounded-lg border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-4">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-ink-secondary leading-relaxed">{obj}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Prerequisites */}
          {course.prerequisites && course.prerequisites.length > 0 && (
            <section>
              <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Before you begin</p>
              <h2 className="font-display text-2xl font-medium tracking-tight text-ink mb-4">Prerequisites</h2>
              <div className="space-y-2.5">
                {course.prerequisites.map((pre, i) => (
                  <div key={i} className="flex items-start gap-2.5 text-sm text-ink-secondary leading-relaxed">
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-coral-500 flex-shrink-0" aria-hidden="true" />
                    {pre}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Course Content / Curriculum */}
          <section id="curriculum" className="scroll-mt-24">
            <div className="flex flex-wrap items-end justify-between gap-2 mb-4">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Syllabus architecture</p>
                <h2 className="font-display text-2xl font-medium tracking-tight text-ink">Course Curriculum</h2>
              </div>
              <p className="font-mono text-[11px] uppercase tracking-wide text-ink-tertiary">
                {course.module_count} modules · {course.lesson_count} lessons
              </p>
            </div>

            {modules ? (
              <div className="rounded-xl border border-border dark:border-white/10 overflow-hidden divide-y divide-border dark:divide-white/10">
                {modules.map((mod, idx) => (
                  <div key={mod.id} className="flex items-center justify-between gap-4 p-4 bg-surface dark:bg-night-500 hover:bg-surface-secondary dark:hover:bg-night-400/40 transition-colors">
                    <div className="flex items-center gap-4 min-w-0">
                      <span className="h-9 w-9 rounded-lg border border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600 flex items-center justify-center font-mono text-xs text-coral-600 dark:text-coral-400 flex-shrink-0">
                        {String(idx + 1).padStart(2, "0")}
                      </span>
                      <div className="min-w-0">
                        <h3 className="font-medium text-sm text-ink truncate">{mod.title}</h3>
                        <p className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary mt-1">
                          {mod.lesson_count} lessons
                          {mod.estimated_duration_minutes ? ` · ${formatDuration(mod.estimated_duration_minutes)}` : ""}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-ink-tertiary flex-shrink-0" aria-hidden="true" />
                  </div>
                ))}
              </div>
            ) : modulesLoading ? (
              <div className="rounded-xl border border-border dark:border-white/10 overflow-hidden divide-y divide-border dark:divide-white/10">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-4 bg-surface dark:bg-night-500">
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
          <div className="lg:sticky lg:top-20">
            <Card padding="md">
              <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Track specification</p>
              <h3 className="font-display text-lg font-medium tracking-tight text-ink mb-4">Course Info</h3>
              <dl className="space-y-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Level</dt>
                  <dd><Badge size="sm" className={difficultyColor(course.difficulty)}>{course.difficulty}</Badge></dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Language</dt>
                  <dd className="text-ink font-medium">{course.language}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Lessons</dt>
                  <dd className="text-ink font-medium">{course.lesson_count}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Duration</dt>
                  <dd className="text-ink font-medium">{formatDuration(course.estimated_duration_minutes)}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Enrolled</dt>
                  <dd className="text-ink font-medium">{formatNumber(course.enrollment_count)}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Access</dt>
                  <dd className="text-ink font-medium">{course.is_free ? "Free" : "Full course"}</dd>
                </div>
              </dl>
              <div className="mt-4 pt-4 border-t border-border dark:border-white/10">
                <Button className="w-full" size="lg" onClick={handleEnroll}>
                  Enroll Now
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Reviews */}
      <section>
        <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-2">{"// "}Community feedback</p>
            <h2 className="font-display text-2xl font-medium tracking-tight text-ink flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-coral-500" aria-hidden="true" /> Student Reviews
            </h2>
          </div>
          {course.rating_count > 0 && <Rating value={course.rating_average} count={course.rating_count} size="md" />}
        </div>

        {/* Write review */}
        {isAuthenticated && (
          <Card padding="md" className="mb-4">
            <h3 className="font-display font-medium text-ink mb-3">Write a review</h3>
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
              className="w-full px-3 py-2 rounded-lg border border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600 text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 mb-3"
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
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded-lg bg-coral-500/10 border border-coral-500/30 flex items-center justify-center text-coral-600 dark:text-coral-400 font-mono font-semibold text-xs">
                      {r.display_name?.[0]?.toUpperCase() || "U"}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-ink leading-tight">{r.display_name}</p>
                      <p className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary">{formatDate(r.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex" aria-label={`${r.rating} out of 5 stars`}>
                    {[1, 2, 3, 4, 5].map((n) => (
                      <Star key={n} className={n <= r.rating ? "h-4 w-4 fill-amber-400 text-amber-400" : "h-4 w-4 text-ink-tertiary"} aria-hidden="true" />
                    ))}
                  </div>
                </div>
                {r.review && <p className="text-sm text-ink-secondary whitespace-pre-wrap leading-relaxed">{r.review}</p>}
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
