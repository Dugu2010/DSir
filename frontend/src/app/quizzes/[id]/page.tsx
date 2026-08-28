"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { quizzes } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { ChevronLeft, CheckCircle, XCircle, Trophy, ClipboardList } from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";
import type { QuizDetail, QuizResult } from "@/lib/types";

export default function QuizPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [result, setResult] = useState<QuizResult | null>(null);

  const { data: quiz, isLoading, error, refetch } = useQuery({
    queryKey: ["quiz", params.id],
    queryFn: () => quizzes.getDetail(params.id),
    enabled: !!params.id,
    retry: 1,
  });

  const submitMutation = useMutation({
    mutationFn: (answers: Record<string, unknown>) => quizzes.submit(params.id, answers),
    onSuccess: (data) => {
      setResult(data);
      if (data.passed) toast.success(`Passed! Score: ${data.score}% 🎉`);
      else toast.error(`Score: ${data.score}% — need ${quiz?.passing_score}% to pass.`);
    },
    onError: () => toast.error("Submission failed. Please try again."),
  });

  if (isLoading || !quiz) {
    if (error) {
      return (
        <ErrorState
          title="Couldn't load this quiz"
          description="Check your connection and try again."
          onRetry={() => refetch()}
        />
      );
    }
    return <PageLoader label="Loading quiz..." />;
  }

  const selectAnswer = (questionId: string, optionId: string, multiple: boolean) => {
    setAnswers((prev) => {
      if (multiple) {
        const current = (prev[questionId] as string[]) || [];
        const next = current.includes(optionId)
          ? current.filter((id) => id !== optionId)
          : [...current, optionId];
        return { ...prev, [questionId]: next };
      }
      return { ...prev, [questionId]: optionId };
    });
  };

  const allAnswered = quiz.questions.every((q) => {
    const a = answers[q.id];
    return Array.isArray(a) ? a.length > 0 : !!a;
  });

  // Results view
  if (result) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center py-8">
          <div className={cn(
            "h-20 w-20 rounded-3xl flex items-center justify-center mx-auto mb-4",
            result.passed ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500",
          )}>
            {result.passed ? <Trophy className="h-10 w-10" /> : <XCircle className="h-10 w-10" />}
          </div>
          <h1 className="font-display text-3xl font-semibold text-ink">
            {result.passed ? "You passed!" : "Not quite yet"}
          </h1>
          <p className="text-ink-secondary mt-1">{quiz.title}</p>
          <div className="flex items-center justify-center gap-8 mt-6">
            <div>
              <p className="text-3xl font-display font-bold text-coral-500">{result.score}%</p>
              <p className="text-xs text-ink-tertiary mt-1">Score</p>
            </div>
            <div>
              <p className="text-3xl font-display font-bold text-ink">{result.correct_answers}/{result.total_questions}</p>
              <p className="text-xs text-ink-tertiary mt-1">Correct</p>
            </div>
            <div>
              <p className="text-3xl font-display font-bold text-amber-500">{result.earned_points}</p>
              <p className="text-xs text-ink-tertiary mt-1">XP earned</p>
            </div>
          </div>
          <div className="flex justify-center gap-3 mt-8">
            <Button variant="outline" onClick={() => { setResult(null); setAnswers({}); }}>
              Retake Quiz
            </Button>
            <Button onClick={() => router.push("/quizzes")}>Back to Quizzes</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-24">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-tertiary dark:hover:bg-white/5"
          aria-label="Go back"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <p className="eyebrow mb-1">Quiz</p>
          <h1 className="font-display text-2xl font-semibold text-ink flex items-center gap-2">
            <ClipboardList className="h-6 w-6 text-coral-500" />
            {quiz.title}
          </h1>
        </div>
        <Badge variant="outline" size="sm">Pass {quiz.passing_score}%</Badge>
      </div>

      {quiz.description && <p className="text-ink-secondary">{quiz.description}</p>}

      <div className="space-y-4">
        {quiz.questions.map((q, idx) => {
          const multiple = q.question_type === "multiple_choice";
          const selected = answers[q.id];
          const isSelected = (oid: string) =>
            multiple ? (selected as string[] || []).includes(oid) : selected === oid;
          return (
            <Card key={q.id} padding="md">
              <div className="flex items-start gap-3 mb-4">
                <span className="h-7 w-7 rounded-lg bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center text-sm font-semibold flex-shrink-0">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-ink">{q.content}</p>
                  <p className="text-xs text-ink-tertiary mt-0.5">
                    {q.points} pts · {multiple ? "Select all that apply" : "Select one"}
                  </p>
                </div>
              </div>
              <div className="space-y-2 pl-10">
                {q.options.map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => selectAnswer(q.id, opt.id, multiple)}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-xl border transition-colors text-sm",
                      isSelected(opt.id)
                        ? "border-coral-500 bg-coral-50 dark:bg-coral-500/10 text-ink font-medium"
                        : "border-border dark:border-white/10 text-ink-secondary hover:border-coral-400/60 hover:bg-surface-secondary dark:hover:bg-white/5",
                    )}
                  >
                    <span className="flex items-center gap-2">
                      {isSelected(opt.id) ? <CheckCircle className="h-4 w-4 text-coral-500" /> : <span className="h-4 w-4 rounded-full border border-ink-tertiary/40" />}
                      {opt.content}
                    </span>
                  </button>
                ))}
              </div>
            </Card>
          );
        })}
      </div>

      <div className="fixed bottom-0 inset-x-0 lg:left-64 bg-surface/90 dark:bg-night-500/90 backdrop-blur-xl border-t border-border dark:border-white/5 p-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <p className="text-sm text-ink-secondary">
            {Object.keys(answers).length}/{quiz.questions.length} answered
          </p>
          <Button
            onClick={() => submitMutation.mutate(answers)}
            loading={submitMutation.isPending}
            disabled={!allAnswered}
          >
            Submit Quiz
          </Button>
        </div>
      </div>
    </div>
  );
}
