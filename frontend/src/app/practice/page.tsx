"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { practice as practiceApi } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { Code2, Bug, Wrench, Zap, Search, Clock, Star, Play, Filter } from "lucide-react";
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

  const { data, isLoading } = useQuery({
    queryKey: ["exercises", difficulty, exerciseType],
    queryFn: () => practiceApi.listExercises({ ...(difficulty && { difficulty }), ...(exerciseType && { exercise_type: exerciseType }) }),
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-ink">Practice Hub</h1>
        <p className="text-ink-secondary mt-1">Sharpen your skills with hands-on coding exercises.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {["", "easy", "medium", "hard"].map((d) => (
          <button
            key={d || "all"}
            onClick={() => setDifficulty(d)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              difficulty === d
                ? "bg-brand-600 text-white"
                : "bg-surface-secondary text-ink-secondary hover:text-ink hover:bg-surface-tertiary border border-border"
            }`}
          >
            {d ? d.charAt(0).toUpperCase() + d.slice(1) : "All Levels"}
          </button>
        ))}
        <div className="w-px h-8 bg-border mx-1 self-center" />
        {["", "code_completion", "debugging", "output_prediction", "refactoring", "bug_fixing"].map((t) => (
          <button
            key={t || "all-types"}
            onClick={() => setExerciseType(t)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              exerciseType === t
                ? "bg-brand-600 text-white"
                : "bg-surface-secondary text-ink-secondary hover:text-ink hover:bg-surface-tertiary border border-border"
            }`}
          >
            {t ? typeLabels[t] || t : "All Types"}
          </button>
        ))}
      </div>

      {/* Exercise Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (<CardSkeleton key={i} />))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((ex) => {
            const Icon = typeIcons[ex.exercise_type] || Code2;
            return (
              <div key={ex.id}>
                <Card hover padding="md" onClick={() => toast("Exercise viewer coming soon!")}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="h-10 w-10 rounded-xl bg-brand-50 dark:bg-brand-950 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-brand-600 dark:text-brand-400" />
                    </div>
                    <div className="flex gap-1.5">
                      <Badge size="sm" className={difficultyColors[ex.difficulty] || ""}>
                        {ex.difficulty}
                      </Badge>
                    </div>
                  </div>
                  <h3 className="font-semibold text-ink mb-1">{ex.title}</h3>
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
                </Card>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <Code2 className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-ink">No exercises found</h3>
          <p className="text-sm text-ink-secondary mt-1">Try adjusting your filters.</p>
        </div>
      )}
    </div>
  );
}
