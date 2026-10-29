"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { revision as revisionApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { Brain, Plus } from "lucide-react";
import type { Flashcard } from "@/lib/types";
import toast from "react-hot-toast";

export default function RevisionPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const { data: dueCards, isLoading: cardsLoading, error: cardsError, refetch: refetchCards } = useQuery({
    queryKey: ["due-flashcards"],
    queryFn: () => revisionApi.getDueFlashcards(),
  });

  const { data: stats } = useQuery({
    queryKey: ["revision-stats"],
    queryFn: () => revisionApi.getStats(),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      revisionApi.reviewFlashcard(cardId, quality),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["due-flashcards"] });
      queryClient.invalidateQueries({ queryKey: ["revision-stats"] });
      setFlipped(false);
    },
  });

  const createMutation = useMutation({
    mutationFn: () => revisionApi.createFlashcard({ front_content: front, back_content: back }),
    onSuccess: () => {
      toast.success("Flashcard created!");
      setFront("");
      setBack("");
      setShowCreate(false);
      queryClient.invalidateQueries({ queryKey: ["due-flashcards"] });
      queryClient.invalidateQueries({ queryKey: ["revision-stats"] });
    },
  });

  const handleReview = (quality: number) => {
    if (dueCards && dueCards[currentCard]) {
      reviewMutation.mutate({ cardId: dueCards[currentCard].id, quality });
      if (currentCard + 1 < dueCards.length) {
        setCurrentCard(currentCard + 1);
      } else {
        setCurrentCard(0);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
              {"// "}No. 18 · Spaced repetition
            </p>
            <h1 className="font-display text-3xl md:text-4xl font-medium tracking-tight text-ink mt-2">Revision</h1>
            <p className="text-ink-secondary mt-1">Review flashcards using spaced repetition.</p>
          </div>
          <Button
            variant={showCreate ? "outline" : "primary"}
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => setShowCreate(!showCreate)}
          >
            New Flashcard
          </Button>
        </div>
        {stats && (
          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
            <div className="bg-surface dark:bg-night-500 px-5 py-4">
              <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Total cards</dt>
              <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{stats.total_cards}</dd>
            </div>
            <div className="bg-surface dark:bg-night-500 px-5 py-4">
              <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Due today</dt>
              <dd className="font-display text-2xl font-medium text-coral-600 dark:text-coral-400 mt-1 tabular-nums">{stats.due_today}</dd>
            </div>
            <div className="bg-surface dark:bg-night-500 px-5 py-4">
              <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">This week</dt>
              <dd className="font-display text-2xl font-medium text-emerald-600 dark:text-emerald-400 mt-1 tabular-nums">{stats.reviewed_this_week}</dd>
            </div>
            <div className="bg-surface dark:bg-night-500 px-5 py-4">
              <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">Avg ease</dt>
              <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{stats.average_ease_factor}</dd>
            </div>
          </dl>
        )}
      </header>

      {/* Create Flashcard */}
      {showCreate && (
        <Card padding="md">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-1">
            {"// "}New card
          </p>
          <h3 className="font-display text-lg font-medium text-ink mb-4">Create Flashcard</h3>
          <div className="space-y-3">
            <Input
              label="Front"
              placeholder="Question or concept..."
              value={front}
              onChange={(e) => setFront(e.target.value)}
            />
            <Input
              label="Back"
              placeholder="Answer or explanation..."
              value={back}
              onChange={(e) => setBack(e.target.value)}
            />
            <Button
              onClick={() => createMutation.mutate()}
              loading={createMutation.isPending}
              disabled={!front || !back}
            >
              Create Card
            </Button>
          </div>
        </Card>
      )}

      {/* Flashcard Viewer */}
      {cardsLoading ? (
        <PageLoader />
      ) : cardsError ? (
        <ErrorState
          title="Failed to load flashcards"
          description="Could not connect to the server. Check your connection and try again."
          onRetry={() => refetchCards()}
        />
      ) : dueCards && dueCards.length > 0 ? (
        <div className="space-y-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary text-center tabular-nums">
            {"// "}Card {currentCard + 1} of {dueCards.length} due today
          </p>

          {/* Card */}
          <button
            onClick={() => setFlipped(!flipped)}
            aria-pressed={flipped}
            className="w-full min-h-64 rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-8 flex items-center justify-center text-center cursor-pointer hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-colors"
          >
            <div className="max-w-md">
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-coral-600 dark:text-coral-400 mb-3">
                {flipped ? "Answer" : "Prompt"}
              </p>
              <p className="font-display text-xl font-medium text-ink leading-relaxed">
                {flipped ? dueCards[currentCard]?.back_content : dueCards[currentCard]?.front_content}
              </p>
              {!flipped && (
                <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-4">Click to reveal answer</p>
              )}
            </div>
          </button>

          {/* Rating buttons */}
          {flipped && (
            <div className="flex flex-wrap justify-center gap-3 animate-fade-in">
              {[
                { quality: 1, label: "Again", color: "border-red-500/30 bg-red-500/10 text-red-600 dark:text-red-400 hover:bg-red-500/20" },
                { quality: 2, label: "Hard", color: "border-orange-500/30 bg-orange-500/10 text-orange-600 dark:text-orange-400 hover:bg-orange-500/20" },
                { quality: 3, label: "Good", color: "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 hover:bg-amber-500/20" },
                { quality: 4, label: "Easy", color: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20" },
              ].map(({ quality, label, color }) => (
                <button
                  key={quality}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleReview(quality);
                  }}
                  className={`px-6 py-3 rounded-full border font-mono text-[11px] uppercase tracking-[0.14em] transition-colors ${color}`}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-16">
          <Brain className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="font-display text-lg font-medium text-ink">No cards due</h3>
          <p className="text-sm text-ink-secondary mt-1">
            You&apos;re all caught up! Create new flashcards or check back later.
          </p>
        </div>
      )}
    </div>
  );
}
