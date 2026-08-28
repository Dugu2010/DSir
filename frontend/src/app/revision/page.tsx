"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { revision as revisionApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { Brain, RotateCw, CheckCircle2, XCircle, ArrowRight, Plus, BarChart3, Clock, Target } from "lucide-react";
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
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p className="eyebrow mb-2 !text-coral-400">No. 05 — Spaced repetition</p>
            <h1 className="font-display text-3xl font-semibold tracking-tight">Revision</h1>
            <p className="text-paper-50/70 dark:text-ink-secondary mt-1">Review flashcards using spaced repetition.</p>
          </div>
          <Button
            variant={showCreate ? "outline" : "primary"}
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => setShowCreate(!showCreate)}
          >
            New Flashcard
          </Button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Card padding="sm" className="text-center">
            <div className="font-display text-2xl font-bold text-ink">{stats.total_cards}</div>
            <div className="text-xs text-ink-tertiary mt-1">Total Cards</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="font-display text-2xl font-bold text-coral-600 dark:text-coral-400">{stats.due_today}</div>
            <div className="text-xs text-ink-tertiary mt-1">Due Today</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="font-display text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.reviewed_this_week}</div>
            <div className="text-xs text-ink-tertiary mt-1">This Week</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="font-display text-2xl font-bold text-ink">{stats.average_ease_factor}</div>
            <div className="text-xs text-ink-tertiary mt-1">Avg Ease</div>
          </Card>
        </div>
      )}

      {/* Create Flashcard */}
      {showCreate && (
        <Card padding="md">
          <p className="eyebrow mb-1">New card</p>
          <h3 className="font-display text-lg font-semibold text-ink mb-4">Create Flashcard</h3>
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
          <div className="text-sm text-ink-tertiary text-center">
            Card {currentCard + 1} of {dueCards.length} due today
          </div>

          {/* Card */}
          <button
            onClick={() => setFlipped(!flipped)}
            aria-pressed={flipped}
            className="w-full min-h-64 rounded-2xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-8 flex items-center justify-center text-center cursor-pointer hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-all duration-300"
          >
            <div className="max-w-md">
              <p className="font-display text-xl text-ink leading-relaxed">
                {flipped ? dueCards[currentCard]?.back_content : dueCards[currentCard]?.front_content}
              </p>
              {!flipped && (
                <p className="text-xs text-ink-tertiary mt-4">Click to reveal answer</p>
              )}
            </div>
          </button>

          {/* Rating buttons */}
          {flipped && (
            <div className="flex flex-wrap justify-center gap-3 animate-fade-in">
              {[
                { quality: 1, label: "Again", color: "bg-red-100 text-red-700 hover:bg-red-200" },
                { quality: 2, label: "Hard", color: "bg-orange-100 text-orange-700 hover:bg-orange-200" },
                { quality: 3, label: "Good", color: "bg-amber-100 text-amber-700 hover:bg-amber-200" },
                { quality: 4, label: "Easy", color: "bg-emerald-100 text-emerald-700 hover:bg-emerald-200" },
              ].map(({ quality, label, color }) => (
                <button
                  key={quality}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleReview(quality);
                  }}
                  className={`px-6 py-3 rounded-xl font-medium text-sm transition-all ${color}`}
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
          <h3 className="font-display text-lg font-semibold text-ink">No cards due</h3>
          <p className="text-sm text-ink-secondary mt-1">
            You&apos;re all caught up! Create new flashcards or check back later.
          </p>
        </div>
      )}
    </div>
  );
}
