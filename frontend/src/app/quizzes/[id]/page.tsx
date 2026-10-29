"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { quizzes } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageLoader, ErrorState } from "@/components/ui/States";
import {
  ChevronLeft, CheckCircle, XCircle, Trophy, ClipboardList, Timer, Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";
import type { QuizResult } from "@/lib/types";

function formatClock(totalSeconds: number) {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function formatSpent(totalSeconds: number) {
  const safe = Math.max(0, Math.round(totalSeconds));
  if (safe < 60) return `${safe}s`;
  return `${Math.floor(safe / 60)}m ${safe % 60}s`;
}

function errorStatus(error: unknown): number | undefined {
  return (error as { status?: number } | null)?.status;
}

function errorMessage(error: unknown): string {
  return error instanceof Error && error.message ? error.message : "Submission failed.";
}

export default function QuizPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [reviewLoading, setReviewLoading] = useState(false);

  // Per-question timing: time accrues to whichever question the learner is
  // currently working on, and is flushed on submission.
  const activeQuestionRef = useRef<string | null>(null);
  const activeSinceRef = useRef<number>(Date.now());
  const questionSecondsRef = useRef<Record<string, number>>({});
  const timingAttemptRef = useRef<string | null>(null);
  const autoSubmittedRef = useRef(false);

  const { data: quiz, isLoading, error, refetch } = useQuery({
    queryKey: ["quiz", params.id],
    queryFn: () => quizzes.getDetail(params.id),
    enabled: !!params.id,
    retry: 1,
  });

  const {
    data: attempt,
    error: attemptError,
    isLoading: attemptLoading,
    refetch: refetchAttempt,
  } = useQuery({
    queryKey: ["quiz-attempt", params.id],
    queryFn: () => quizzes.startAttempt(params.id),
    enabled: !!quiz && quiz.can_attempt && !result,
    retry: false,
    staleTime: Infinity,
    gcTime: 0,
    refetchOnWindowFocus: false,
  });

  const submitMutation = useMutation({
    mutationFn: (payload: {
      answers: Record<string, unknown>;
      attempt_id?: string;
      question_times?: Record<string, number>;
    }) => quizzes.submit(params.id, payload),
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ["quiz", params.id] });
      queryClient.invalidateQueries({ queryKey: ["quizzes"] });
      if (data.passed) toast.success(`Passed! Score: ${data.score}% 🎉`);
      else toast.error(`Score: ${data.score}% — need ${quiz?.passing_score}% to pass.`);
    },
    onError: (err: unknown) => {
      const status = errorStatus(err);
      toast.error(status === 409 ? errorMessage(err) : "Submission failed. Please try again.");
      if (status === 409) {
        refetchAttempt();
        refetch();
      }
    },
  });

  useEffect(() => {
    if (!attempt || result) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [attempt, result]);

  useEffect(() => {
    if (!attempt || timingAttemptRef.current === attempt.attempt_id) return;
    timingAttemptRef.current = attempt.attempt_id;
    activeQuestionRef.current = quiz?.questions[0]?.id ?? null;
    activeSinceRef.current = Date.now();
    questionSecondsRef.current = {};
    autoSubmittedRef.current = false;
  }, [attempt, quiz]);

  const secondsLeft = attempt?.expires_at
    ? Math.max(0, Math.ceil((new Date(attempt.expires_at).getTime() - now) / 1000))
    : null;
  const elapsedSeconds = attempt
    ? Math.max(0, Math.floor((now - new Date(attempt.started_at).getTime()) / 1000))
    : 0;
  const timeIsUp = secondsLeft !== null && secondsLeft <= 0;

  const collectQuestionTimes = () => {
    const times = { ...questionSecondsRef.current };
    const active = activeQuestionRef.current;
    if (active) {
      times[active] = (times[active] ?? 0) + (Date.now() - activeSinceRef.current) / 1000;
    }
    return Object.fromEntries(
      Object.entries(times).map(([questionId, seconds]) => [
        questionId,
        Math.max(1, Math.round(seconds)),
      ]),
    );
  };

  const submitAnswers = () => {
    if (!attempt || submitMutation.isPending) return;
    submitMutation.mutate({
      answers,
      attempt_id: attempt.attempt_id,
      question_times: collectQuestionTimes(),
    });
  };

  // Auto-submit when the countdown hits zero so a timed attempt is graded
  // rather than silently expiring.
  useEffect(() => {
    if (!attempt?.expires_at || result || secondsLeft === null || secondsLeft > 0) return;
    if (autoSubmittedRef.current) return;
    autoSubmittedRef.current = true;
    submitMutation.mutate({
      answers,
      attempt_id: attempt.attempt_id,
      question_times: collectQuestionTimes(),
    });
    // collectQuestionTimes and submitMutation read refs/state from this render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft, attempt, result]);

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
    if (timeIsUp) return;
    if (activeQuestionRef.current !== questionId) {
      const previous = activeQuestionRef.current;
      if (previous) {
        questionSecondsRef.current[previous] =
          (questionSecondsRef.current[previous] ?? 0) +
          (Date.now() - activeSinceRef.current) / 1000;
      }
      activeQuestionRef.current = questionId;
      activeSinceRef.current = Date.now();
    }
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

  const handleRetake = () => {
    setResult(null);
    setAnswers({});
    questionSecondsRef.current = {};
    activeQuestionRef.current = null;
    autoSubmittedRef.current = false;
    timingAttemptRef.current = null;
    queryClient.removeQueries({ queryKey: ["quiz-attempt", params.id] });
    refetch();
  };

  const handleReviewLast = async () => {
    setReviewLoading(true);
    try {
      setResult(await quizzes.getResults(params.id));
    } catch {
      toast.error("Couldn't load your last attempt.");
    } finally {
      setReviewLoading(false);
    }
  };

  // Results view
  if (result) {
    const attemptsLeft = result.attempts_remaining;
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 text-center px-6 py-10">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
          <div className={cn(
            "h-16 w-16 rounded-xl border flex items-center justify-center mx-auto mb-4",
            result.passed
              ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-500"
              : "border-red-500/30 bg-red-500/10 text-red-500",
          )}>
            {result.passed ? <Trophy className="h-8 w-8" /> : <XCircle className="h-8 w-8" />}
          </div>
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}Assessment graded
          </p>
          <h1 className="font-display text-3xl font-medium text-ink mt-2">
            {result.passed ? "You passed." : "Not quite yet."}
          </h1>
          <p className="text-ink-secondary mt-1">{quiz.title}</p>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-4 mt-6">
            <div>
              <p className="text-3xl font-display font-medium text-coral-500 tabular-nums">{result.score}%</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">Score</p>
            </div>
            <div>
              <p className="text-3xl font-display font-medium text-ink tabular-nums">{result.correct_answers}/{result.total_questions}</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">Correct</p>
            </div>
            <div>
              <p className="text-3xl font-display font-medium text-amber-500 tabular-nums">{result.xp_earned}</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">XP earned</p>
            </div>
            <div>
              <p className="text-3xl font-display font-medium text-ink tabular-nums">{formatClock(result.duration_seconds)}</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">Time taken</p>
            </div>
          </div>
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-4">
            Attempt {result.attempt_number}
            {quiz.max_attempts ? ` of ${quiz.max_attempts}` : ""} · Best {result.best_score}%
            {attemptsLeft === 0 ? " · no attempts left" : ""}
          </p>
          {result.xp_earned === 0 && (
            <p className="text-xs text-ink-tertiary mt-1 max-w-md mx-auto">
              No new XP this time — retakes only award XP when you beat your best score.
            </p>
          )}
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            <Button
              variant="outline"
              onClick={handleRetake}
              disabled={attemptsLeft === 0}
              title={attemptsLeft === 0 ? "You've used every attempt for this quiz." : undefined}
            >
              {attemptsLeft === 0 ? "No Attempts Left" : "Retake Quiz"}
            </Button>
            <Button onClick={() => router.push("/quizzes")}>Back to Quizzes</Button>
          </div>
          {attemptsLeft !== null && attemptsLeft > 0 && (
            <p className="text-xs text-ink-tertiary mt-3">
              {attemptsLeft} {attemptsLeft === 1 ? "attempt" : "attempts"} remaining
            </p>
          )}
        </div>

        {result.feedback && result.feedback.length > 0 && (
          <div className="space-y-3 text-left">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400">
              {"// "}Post-attempt review
            </p>
            <h2 className="font-display text-xl font-medium text-ink">Review your answers</h2>
            <p className="text-sm text-ink-secondary -mt-2">
              The explanations below are shown only after you submit.
            </p>
            {result.feedback.map((item, index) => {
              const question = quiz.questions.find((q) => q.id === item.question_id);
              const correctOptions = (question?.options ?? []).filter((option) =>
                item.correct_option_ids.includes(option.id),
              );
              const spent = result.question_times?.[item.question_id];
              return (
                <Card
                  key={item.question_id}
                  padding="md"
                  className={cn(
                    "border",
                    item.correct
                      ? "border-emerald-500/30"
                      : "border-red-500/30",
                  )}
                >
                  <div className="flex items-start gap-3">
                    {item.correct ? (
                      <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" aria-label="Correct" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" aria-label="Incorrect" />
                    )}
                    <div className="min-w-0 flex-1 space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm font-medium text-ink break-words">
                          {index + 1}. {item.question}
                        </p>
                        {typeof spent === "number" && (
                          <span
                            className="text-[11px] text-ink-tertiary whitespace-nowrap shrink-0 flex items-center gap-1"
                            title="Time spent on this question"
                            aria-label={`Time spent on this question: ${formatSpent(spent)}`}
                          >
                            <Timer className="h-3 w-3" /> {formatSpent(spent)}
                          </span>
                        )}
                      </div>
                      {!item.correct && correctOptions.length > 0 && (
                        <p className="text-sm text-emerald-700 dark:text-emerald-400 break-words">
                          Correct answer: {correctOptions.map((option) => option.content).join(", ")}
                        </p>
                      )}
                      {!item.correct && item.selected_option_ids.length === 0 && (
                        <p className="text-xs text-ink-tertiary">You left this question unanswered.</p>
                      )}
                      {item.explanation && (
                        <p className="text-sm text-ink-secondary leading-relaxed break-words">
                          {item.explanation}
                        </p>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // No attempts left, or the limit was hit between page load and start.
  if (!quiz.can_attempt || errorStatus(attemptError) === 409) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card padding="lg" className="text-center space-y-4">
          <div className="h-16 w-16 rounded-xl border border-border dark:border-white/10 bg-surface-secondary dark:bg-white/5 flex items-center justify-center mx-auto">
            <Lock className="h-8 w-8 text-ink-tertiary" />
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-tertiary">{"// "}Attempt quota exhausted</p>
            <h1 className="font-display text-2xl font-medium text-ink mt-1">No attempts left</h1>
            <p className="text-sm text-ink-secondary mt-1">
              {quiz.title}
            </p>
          </div>
          <p className="text-sm text-ink-secondary max-w-md mx-auto">
            You&apos;ve used all {quiz.max_attempts ?? quiz.attempts_used} attempts for this quiz.
            {quiz.best_score > 0 && ` Your best score is ${quiz.best_score}%.`}
          </p>
          <div className="flex flex-wrap justify-center gap-3 pt-2">
            <Button variant="outline" onClick={handleReviewLast} loading={reviewLoading}>
              Review Last Attempt
            </Button>
            <Button onClick={() => router.push("/quizzes")}>Back to Quizzes</Button>
          </div>
        </Card>
      </div>
    );
  }

  if (attemptLoading || !attempt) {
    if (attemptError) {
      return (
        <ErrorState
          title="Couldn't start this attempt"
          description={errorMessage(attemptError)}
          onRetry={() => refetchAttempt()}
        />
      );
    }
    return <PageLoader label="Starting attempt..." />;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-28">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-tertiary dark:hover:bg-white/5"
          aria-label="Go back"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
          — Assessment // Quiz runner —
        </p>
      </div>

      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary flex items-center gap-1.5">
                <ClipboardList className="h-3.5 w-3.5 text-coral-500" /> Timed assessment
              </p>
              <h1 className="font-display text-xl sm:text-2xl font-medium text-ink mt-2 leading-snug">
                {quiz.title}
              </h1>
              {quiz.description && (
                <p className="text-sm text-ink-secondary mt-1 max-w-2xl">{quiz.description}</p>
              )}
            </div>
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-coral-600 dark:text-coral-400 border border-coral-500/30 bg-coral-500/5 rounded-full px-3 py-1 shrink-0 tabular-nums">
              Pass {quiz.passing_score}%
            </span>
          </div>
        </div>
        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
          <div className="bg-surface dark:bg-night-500 px-4 py-3">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Attempt</dt>
            <dd className="text-sm text-ink mt-0.5 tabular-nums">
              {attempt.attempts_used + 1}
              {attempt.max_attempts ? ` of ${attempt.max_attempts}` : ""}
            </dd>
          </div>
          <div className="bg-surface dark:bg-night-500 px-4 py-3">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
              {secondsLeft !== null ? "Remaining" : "Elapsed"}
            </dt>
            <dd
              className={cn(
                "text-sm mt-0.5 tabular-nums font-mono",
                secondsLeft !== null && secondsLeft <= 60 ? "text-red-600 dark:text-red-400" : "text-ink",
              )}
            >
              {secondsLeft !== null ? formatClock(secondsLeft) : formatClock(elapsedSeconds)}
            </dd>
          </div>
          <div className="bg-surface dark:bg-night-500 px-4 py-3">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Record</dt>
            <dd className="text-sm text-ink mt-0.5 tabular-nums">
              {attempt.best_score > 0 ? `Best ${attempt.best_score}%` : "No record"}
            </dd>
          </div>
          <div className="bg-surface dark:bg-night-500 px-4 py-3">
            <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Progress</dt>
            <dd className="text-sm text-ink mt-0.5 tabular-nums">
              {Object.keys(answers).length} of {quiz.questions.length} answered
            </dd>
          </div>
        </dl>
      </header>

      {timeIsUp && (
        <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
          <Timer className="h-4 w-4" /> Time&apos;s up — submitting your answers.
        </p>
      )}

      <div className="space-y-4">
        {quiz.questions.map((q, idx) => {
          // Current question types all have exactly one correct option. Only
          // multi-select types (not present in the enum yet) would allow more.
          const multiple = false;
          const selected = answers[q.id];
          const isSelected = (oid: string) =>
            multiple ? (selected as string[] || []).includes(oid) : selected === oid;
          return (
            <Card key={q.id} padding="md">
              <div className="flex items-start gap-3 mb-4">
                <span className="h-7 w-7 rounded-md border border-coral-500/30 bg-coral-500/10 text-coral-600 dark:text-coral-400 flex items-center justify-center font-mono text-[11px] flex-shrink-0 tabular-nums">
                  {String(idx + 1).padStart(2, "0")}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-ink leading-relaxed break-words">{q.content}</p>
                  <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">
                    {q.points} pts · Choose one answer
                  </p>
                </div>
              </div>
              <div className="space-y-2 sm:pl-10">
                {q.options.map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => selectAnswer(q.id, opt.id, multiple)}
                    disabled={timeIsUp}
                    className={cn(
                      "w-full text-left px-4 py-3 rounded-lg border transition-colors text-sm",
                      isSelected(opt.id)
                        ? "border-coral-500 bg-coral-50 dark:bg-coral-500/10 text-ink font-medium"
                        : "border-border dark:border-white/10 text-ink-secondary hover:border-coral-400/60 hover:bg-surface-secondary dark:hover:bg-white/5",
                      timeIsUp && "opacity-60 cursor-not-allowed",
                    )}
                  >
                    <span className="flex items-center gap-2">
                      {isSelected(opt.id) ? <CheckCircle className="h-4 w-4 text-coral-500 shrink-0" /> : <span className="h-4 w-4 rounded-full border border-ink-tertiary/40 shrink-0" />}
                      <span className="break-words">{opt.content}</span>
                    </span>
                  </button>
                ))}
              </div>
            </Card>
          );
        })}
      </div>

      <div className="fixed bottom-0 inset-x-0 lg:left-64 bg-surface/90 dark:bg-night-500/90 backdrop-blur-xl border-t border-border dark:border-white/5 p-4">
        <div className="max-w-3xl mx-auto pb-[env(safe-area-inset-bottom)]">
          <div className="h-1 rounded-full bg-surface-tertiary dark:bg-white/10 overflow-hidden mb-3" aria-hidden="true">
            <div
              className="h-full bg-coral-500 transition-all"
              style={{ width: `${Math.round((Object.keys(answers).length / quiz.questions.length) * 100)}%` }}
            />
          </div>
          <div className="flex items-center justify-between gap-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary tabular-nums">
              {Object.keys(answers).length}/{quiz.questions.length} answered
            </p>
            <Button
              onClick={submitAnswers}
              loading={submitMutation.isPending}
              disabled={!allAnswered && !timeIsUp}
            >
              {timeIsUp ? "Submit Answers" : "Submit Quiz"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
