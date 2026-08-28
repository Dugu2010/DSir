"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { quizzes } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { ClipboardList, ChevronRight, Timer, HelpCircle, Award } from "lucide-react";
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

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <p className="eyebrow mb-2">Assessment</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
          <ClipboardList className="h-8 w-8 text-coral-500" />
          Quizzes
        </h1>
        <p className="text-ink-secondary mt-1">
          Test your knowledge and earn XP for correct answers.
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="No quizzes yet"
          description="Quizzes will appear here once they're published."
          icon={<ClipboardList className="h-8 w-8" />}
        />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {items.map((quiz) => (
            <Link key={quiz.id} href={`/quizzes/${quiz.id}`}>
              <Card hover padding="md" className="h-full">
                <div className="flex items-start justify-between mb-3">
                  <Badge variant="outline" size="sm">{quiz.question_count} questions</Badge>
                  <Badge size="sm" className="bg-coral-500/10 text-coral-700 dark:text-coral-400 border border-coral-500/30">
                    Pass {quiz.passing_score}%
                  </Badge>
                </div>
                <h3 className="font-display font-semibold text-ink mb-1">{quiz.title}</h3>
                <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{quiz.description}</p>
                {quiz.course_title && (
                  <p className="text-xs font-mono text-ink-tertiary mb-2">{quiz.course_title}</p>
                )}
                <div className="flex items-center gap-4 text-xs text-ink-tertiary">
                  <span className="flex items-center gap-1">
                    <HelpCircle className="h-3.5 w-3.5" /> {quiz.question_count} Qs
                  </span>
                  {quiz.time_limit_minutes && (
                    <span className="flex items-center gap-1">
                      <Timer className="h-3.5 w-3.5" /> {quiz.time_limit_minutes} min
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-coral-600 dark:text-coral-400 font-medium ml-auto">
                    Start <ChevronRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
