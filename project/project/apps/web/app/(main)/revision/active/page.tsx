"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchDueRevisions, fetchAllConceptsMap, submitReview } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardTitle } from "@/components/ui/card";

export default function ActiveRecallPage() {
  const [index, setIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [conceptMap, setConceptMap] = useState<Record<string, { title: string; slug: string }>>({});

  const { data: due, isLoading } = useQuery({
    queryKey: ["revision-due"],
    queryFn: fetchDueRevisions,
  });

  useEffect(() => {
    fetchAllConceptsMap().then(setConceptMap).catch(() => {});
  }, []);

  const current = due?.[index];
  const conceptName = current
    ? conceptMap[current.concept_id]?.title ?? current.concept_id.slice(0, 8) + "..."
    : "";

  const reviewMutation = useMutation({
    mutationFn: ({ conceptId, quality }: { conceptId: string; quality: number }) =>
      submitReview(conceptId, quality),
  });

  const handleQuality = async (quality: number) => {
    if (!current) return;
    await reviewMutation.mutateAsync({ conceptId: current.concept_id, quality });
    setShowAnswer(false);
    setIndex((prev) => prev + 1);
  };

  if (isLoading) {
    return <div className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />;
  }

  if (!due || due.length === 0 || index >= due.length) {
    return (
      <Card className="text-center">
        <CardTitle>All caught up!</CardTitle>
        <p className="mt-2 text-slate-600 dark:text-slate-400">No concepts due for review right now.</p>
      </Card>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <div className="flex items-center justify-between">
          <CardTitle>Active Recall</CardTitle>
          <span className="text-sm text-slate-500 dark:text-slate-400">
            {index + 1} / {due.length}
          </span>
        </div>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Concept: {conceptName}</p>

        <div className="mt-6">
          <p className="text-lg font-medium text-slate-900 dark:text-white">
            {showAnswer
              ? "Compare your recall with your notes or the original lesson. Rate how well you remembered the concept."
              : "Recall everything you know about this concept, then reveal the answer."}
          </p>

          {!showAnswer && (
            <Button onClick={() => setShowAnswer(true)} className="mt-6 w-full">
              Show Answer
            </Button>
          )}

          {showAnswer && (
            <div className="mt-6 space-y-3">
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">How well did you know it?</p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {[1, 2, 3, 4].map((quality) => (
                  <Button
                    key={quality}
                    onClick={() => handleQuality(quality)}
                    variant="secondary"
                    loading={reviewMutation.isPending}
                  >
                    {quality === 1 ? "Again" : quality === 2 ? "Hard" : quality === 3 ? "Good" : "Easy"}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
