"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchDueRevisions, fetchStrengthsWeaknesses, fetchAllConceptsMap } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { RotateCcw } from "lucide-react";

export default function RevisionPage() {
  const [conceptMap, setConceptMap] = useState<Record<string, { title: string; slug: string }>>({});

  const {
    data: due,
    isLoading: dueLoading,
    error: dueError,
    refetch: refetchDue,
  } = useQuery({
    queryKey: ["revision-due"],
    queryFn: fetchDueRevisions,
  });

  const {
    data: masteryStats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["strengths-weaknesses"],
    queryFn: fetchStrengthsWeaknesses,
  });

  useEffect(() => {
    fetchAllConceptsMap().then(setConceptMap).catch(() => {});
  }, []);

  const conceptName = (id: string) => conceptMap[id]?.title ?? id.slice(0, 8) + "...";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Revision Dashboard</h1>
        <p className="text-muted-foreground">Keep concepts fresh with spaced repetition.</p>
      </div>

      {(dueError || statsError) && (
        <ErrorMessage>
          Failed to load revision data.{" "}
          <Button onClick={() => { refetchDue(); refetchStats(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Due Today</h2>
          {dueLoading ? (
            <RevisionSkeleton count={3} />
          ) : due && due.length > 0 ? (
            <ul className="mt-4 space-y-3">
              {due.map((item) => (
                <li
                  key={item.concept_id}
                  className="flex items-center justify-between rounded-xl border border-border bg-background p-4"
                >
                  <div>
                    <span className="font-medium text-foreground">
                      {conceptName(item.concept_id)}
                    </span>
                    <p className="text-xs text-muted-foreground">
                      Due {new Date(item.due_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link
                    href={`/revision/active?concept=${item.concept_id}`}
                    className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
                  >
                    Review
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              icon={<RotateCcw className="h-6 w-6" />}
              title="Nothing due today"
              description="You're all caught up. Come back tomorrow for more reviews."
            />
          )}
        </section>

        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Weak Concepts</h2>
          {statsLoading ? (
            <RevisionSkeleton count={3} />
          ) : masteryStats?.weaknesses.length ? (
            <ul className="mt-4 space-y-3">
              {masteryStats.weaknesses.slice(0, 5).map((item) => (
                <li
                  key={item.concept_id}
                  className="rounded-xl border border-border bg-background p-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium text-foreground">
                        {conceptName(item.concept_id)}
                      </span>
                      <p className="text-xs text-muted-foreground">
                        Confidence: {item.confidence}%
                      </p>
                    </div>
                    <span className="text-sm text-destructive">{item.score}%</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              icon={<RotateCcw className="h-6 w-6" />}
              title="No weak concepts"
              description="Your mastery is looking solid. Keep practicing to maintain it."
            />
          )}
        </section>
      </div>

      <section className="rounded-2xl border border-border bg-card p-6">
        <h2 className="text-lg font-semibold text-card-foreground">Active Recall</h2>
        <p className="mt-2 text-muted-foreground">
          Start a focused revision session to test your knowledge with AI-generated problems.
        </p>
        <Link
          href="/revision/active"
          className="mt-4 inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 font-semibold text-primary-foreground transition hover:bg-primary/90"
        >
          Start Session
        </Link>
      </section>
    </div>
  );
}

function RevisionSkeleton({ count }: { count: number }) {
  return (
    <div className="mt-4 space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
      ))}
    </div>
  );
}
