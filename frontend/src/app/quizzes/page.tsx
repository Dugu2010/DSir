"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { quizzes } from "@/lib/api";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { ClipboardList, ArrowRight } from "lucide-react";
import type { QuizListItem } from "@/lib/types";

export default function QuizzesPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["quizzes"],
    queryFn: () => quizzes.list(),
  });

  if (isLoading) return <PageLoader label="Loading quizzes..." />;
  if (error || !data) {
    return (
      <ErrorState
        title="Couldn't load quizzes"
        description="Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  const items: QuizListItem[] = data.items;
  const totalQuestions = items.reduce((sum, quiz) => sum + quiz.question_count, 0);
  const averagePass = items.length
    ? Math.round(items.reduce((sum, quiz) => sum + quiz.passing_score, 0) / items.length)
    : 0;
  const timedQuizzes = items.filter((quiz) => !!quiz.time_limit_minutes).length;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 05 · Assessments &amp; benchmarks
          </p>
          <h1 className="font-display text-3xl md:text-5xl font-medium tracking-tight leading-[1.08] text-ink mt-3">
            Quizzes &amp; Skill{" "}
            <span className="italic text-coral-600 dark:text-coral-400">Benchmarks.</span>
          </h1>
          <p className="text-ink-secondary mt-3 max-w-2xl">
            Test your knowledge under a fixed clock. Attempts are limited, and retakes only earn XP
            when you beat your best score.
          </p>
        </div>
        {items.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
            {[
              { label: "Catalog", value: `${items.length}`, suffix: "quizzes" },
              { label: "Depth", value: `${totalQuestions}`, suffix: "questions" },
              { label: "Pass mark", value: `${averagePass}%`, suffix: "average" },
              { label: "Timed", value: `${timedQuizzes}`, suffix: `of ${items.length}` },
            ].map((stat) => (
              <div key={stat.label} className="bg-surface dark:bg-night-500 px-5 py-4">
                <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">
                  {stat.label}
                </p>
                <p className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">
                  {stat.value}
                </p>
                <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
                  {stat.suffix}
                </p>
              </div>
            ))}
          </div>
        )}
      </header>

      {items.length === 0 ? (
        <EmptyState
          title="No quizzes yet"
          description="Quizzes will appear here once they're published."
          icon={<ClipboardList className="h-8 w-8" />}
        />
      ) : (
        <section>
          <div className="flex items-center justify-between mb-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">
              {"// "}All assessments
            </p>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">
              {String(items.length).padStart(2, "0")} tracks
            </p>
          </div>
          <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 divide-y divide-border dark:divide-white/10 overflow-hidden">
            {items.map((quiz, index) => (
              <Link
                key={quiz.id}
                href={`/quizzes/${quiz.id}`}
                className="group grid gap-4 p-5 sm:p-6 sm:grid-cols-[1fr_auto] sm:items-start hover:bg-surface-secondary dark:hover:bg-white/[0.03] transition-colors"
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-2">
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400">
                      Track // {String(index + 1).padStart(2, "0")}
                    </span>
                    {quiz.course_title && (
                      <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary truncate">
                        {quiz.course_title}
                      </span>
                    )}
                  </div>
                  <h3 className="font-display text-lg sm:text-xl font-medium text-ink leading-snug group-hover:text-coral-700 dark:group-hover:text-coral-400 transition-colors">
                    {quiz.title}
                  </h3>
                  {quiz.description && (
                    <p className="text-sm text-ink-secondary mt-1 line-clamp-2">{quiz.description}</p>
                  )}
                  <dl className="grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-3 mt-4">
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Length</dt>
                      <dd className="text-sm text-ink mt-0.5 tabular-nums">{quiz.question_count} questions</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Timer</dt>
                      <dd className="text-sm text-ink mt-0.5 tabular-nums">
                        {quiz.time_limit_minutes ? `${quiz.time_limit_minutes} min` : "Untimed"}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Pass mark</dt>
                      <dd className="text-sm text-ink mt-0.5 tabular-nums">{quiz.passing_score}%</dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Quota</dt>
                      <dd className="text-sm text-ink mt-0.5 tabular-nums">
                        {quiz.max_attempts ? `${quiz.max_attempts} attempts` : "Unlimited"}
                      </dd>
                    </div>
                  </dl>
                </div>
                <span className="inline-flex items-center gap-1.5 self-end sm:self-center font-mono text-[11px] uppercase tracking-[0.14em] text-coral-600 dark:text-coral-400 group-hover:gap-2.5 transition-all shrink-0">
                  Start quiz <ArrowRight className="h-3.5 w-3.5" />
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
