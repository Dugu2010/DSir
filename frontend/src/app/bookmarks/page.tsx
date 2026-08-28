"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { BookMarked, BookOpen, Code2, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

export default function BookmarksPage() {
  const queryClient = useQueryClient();

  const { data: bookmarks, isLoading, error, refetch } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: () => users.getBookmarks(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => users.deleteBookmark(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
      toast.success("Bookmark removed");
    },
    onError: () => toast.error("Failed to remove bookmark"),
  });

  if (isLoading) return <PageLoader />;
  if (error) {
    return (
      <ErrorState
        title="Failed to load bookmarks"
        description="Could not connect to the server. Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <p className="eyebrow mb-2">Saved for later</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
          <BookMarked className="h-8 w-8 text-coral-600 dark:text-coral-400" />
          Bookmarks
        </h1>
        <p className="text-ink-secondary mt-1">Your saved lessons and exercises.</p>
      </div>

      {bookmarks && bookmarks.length > 0 ? (
        <div className="space-y-2">
          {bookmarks.map((b: { id: string; lesson_id?: string; exercise_id?: string; note?: string; created_at: string }) => (
            <Card key={b.id} padding="md" className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-coral-50 dark:bg-coral-500/10 flex items-center justify-center">
                  {b.lesson_id ? (
                    <BookOpen className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                  ) : (
                    <Code2 className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-ink">
                    {b.lesson_id ? "Lesson" : "Exercise"}
                  </p>
                  {b.note && <p className="text-xs text-ink-tertiary mt-0.5">{b.note}</p>}
                  <p className="text-xs text-ink-tertiary mt-0.5">
                    {new Date(b.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteMutation.mutate(b.id)}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-500/10"
                  aria-label={`Remove bookmark${b.note ? `: ${b.note}` : ""}`}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <BookMarked className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="font-display text-lg font-semibold text-ink">No bookmarks yet</h3>
          <p className="text-sm text-ink-secondary mt-1">Bookmark lessons and exercises to save them for later.</p>
        </div>
      )}
    </div>
  );
}
