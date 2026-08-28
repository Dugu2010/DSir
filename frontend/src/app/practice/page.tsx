"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import { practice as practiceApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/States";
import { Code2, Bug, Wrench, Zap, Search, Clock, Star, Play, Filter, ArrowRight } from "lucide-react";
import type { Exercise } from "@/lib/types";
import toast from "react-hot-toast";

const typeIcons: Record<string, React.ElementType> = {
  output_prediction: Zap,
  debugging: Bug,
  code_completion: Code2,
  bug_fixing: Bug,
  refactoring: Wrench,
  optimization: Zap,
};

const typeLabels: Record<string, string> = {
  output_prediction: "Output Prediction",
  debugging: "Debugging",
  code_completion: "Code Completion",
  bug_fixing: "Bug Fixing",
  refactoring: "Refactoring",
  optimization: "Optimization",
};

const difficultyColors: Record<string, string> = {
  easy: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  hard: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function PracticePage() {
  const [difficulty, setDifficulty] = useState("");
  const [exerciseType, setExerciseType] = useState("");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["exercises", difficulty, exerciseType],
    queryFn: () => practiceApi.listExercises({ ...(difficulty && { difficulty }), ...(exerciseType && { exercise_type: exerciseType }) }),
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 md:p-10 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <p className="eyebrow mb-3 !text-coral-400">No. 04 — Practice</p>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight">Practice Hub</h1>
        <p className="text-paper-50/70 dark:text-ink-secondary mt-1 max-w-xl">Sharpen your skills with hands-on coding exercises.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Filter exercises">
        {["", "easy", "medium", "hard"].map((d) => (
          <button
            key={d || "all"}
            onClick={() => setDifficulty(d)}
            aria-pressed={difficulty === d}
            className={`px-3 py-1.5 rounded-full text-xs font-mono font-medium transition-all ${
              difficulty === d
                ? "bg-coral-500 text-night-600"
                : "bg-surface-tertiary text-ink-secondary hover:text-ink hover:bg-coral-50 dark:hover:bg-coral-500/10 dark:hover:text-coral-400 border border-border dark:border-white/10"
            }`}
          >
            {d ? d.charAt(0).toUpperCase() + d.slice(1) : "All Levels"}
          </button>
        ))}
        <div className="w-px h-8 bg-border dark:bg-white/10 mx-1 self-center" aria-hidden="true" />
        {["", "code_completion", "debugging", "output_prediction", "refactoring", "bug_fixing"].map((t) => (
          <button
            key={t || "all-types"}
            onClick={() => setExerciseType(t)}
            aria-pressed={exerciseType === t}
            className={`px-3 py-1.5 rounded-full text-xs font-mono font-medium transition-all ${
              exerciseType === t
                ? "bg-coral-500 text-night-600"
                : "bg-surface-tertiary text-ink-secondary hover:text-ink hover:bg-coral-50 dark:hover:bg-coral-500/10 dark:hover:text-coral-400 border border-border dark:border-white/10"
            }`}
          >
            {t ? typeLabels[t] || t : "All Types"}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <ErrorState
          title="Failed to load exercises"
          description="Could not connect to the server. Check your connection and try again."
          onRetry={() => refetch()}
        />
      )}

      {/* Exercise Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (<CardSkeleton key={i} />))}
        </div>
      ) : !error && data && data.items.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((ex) => {
            const Icon = typeIcons[ex.exercise_type] || Code2;
            return (
              <Link key={ex.id} href={`/practice/${ex.id}`} className="group block">
                <Card hover padding="md" className="h-full">
                  <div className="flex items-start justify-between mb-3">
                    <div className="h-10 w-10 rounded-xl bg-coral-50 dark:bg-coral-500/10 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                    </div>
                    <div className="flex gap-1.5">
                      <Badge size="sm" className={difficultyColors[ex.difficulty] || ""}>
                        {ex.difficulty}
                      </Badge>
                    </div>
                  </div>
                  <h3 className="font-display font-semibold text-ink mb-1 group-hover:text-coral-700 dark:group-hover:text-coral-400 transition-colors">{ex.title}</h3>
                  <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{ex.description}</p>
                  <div className="flex items-center gap-3 text-xs text-ink-tertiary">
                    <span className="flex items-center gap-1">
                      <Star className="h-3 w-3" /> {ex.points} XP
                    </span>
                    {ex.estimated_duration_minutes && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {ex.estimated_duration_minutes} min
                      </span>
                    )}
                    <Badge size="sm" variant="outline">{typeLabels[ex.exercise_type] || ex.exercise_type}</Badge>
                  </div>
                  {ex.skill_tags && ex.skill_tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {ex.skill_tags.map((tag: string) => (
                        <Badge key={tag} size="sm" variant="outline">{tag}</Badge>
                      ))}
                    </div>
                  )}
                  <div className="mt-4 flex items-center gap-1 text-sm font-medium text-coral-600 dark:text-coral-400">
                    Start Exercise <ArrowRight className="h-3.5 w-3.5" />
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : !error ? (
        <div className="text-center py-16">
          <Code2 className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="font-display text-lg font-semibold text-ink">No exercises found</h3>
          <p className="text-sm text-ink-secondary mt-1">Try adjusting your filters.</p>
        </div>
      ) : null}
    </div>
  );
}
