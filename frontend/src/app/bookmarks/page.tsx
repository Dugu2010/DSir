"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageLoader } from "@/components/ui/States";
import { BookMarked, BookOpen, Code2, Trash2, ExternalLink } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";

export default function BookmarksPage() {
  const queryClient = useQueryClient();

  const { data: bookmarks, isLoading } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: () => users.getBookmarks(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => users.deleteBookmark(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
      toast.success("Bookmark removed");
    },
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-ink flex items-center gap-2">
          <BookMarked className="h-8 w-8 text-brand-600" />
          Bookmarks
        </h1>
        <p className="text-ink-secondary mt-1">Your saved lessons and exercises.</p>
      </div>

      {bookmarks && bookmarks.length > 0 ? (
        <div className="space-y-2">
          {bookmarks.map((b: { id: string; lesson_id?: string; exercise_id?: string; note?: string; created_at: string }) => (
            <Card key={b.id} padding="md" className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-brand-50 dark:bg-brand-950 flex items-center justify-center">
                  {b.lesson_id ? (
                    <BookOpen className="h-5 w-5 text-brand-600" />
                  ) : (
                    <Code2 className="h-5 w-5 text-brand-600" />
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
                {b.lesson_id && (
                  <Link href={`/courses/python-programming/learn`}>
                    <Button variant="ghost" size="sm" leftIcon={<ExternalLink className="h-4 w-4" />}>
                      Open
                    </Button>
                  </Link>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteMutation.mutate(b.id)}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50"
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
          <h3 className="text-lg font-semibold text-ink">No bookmarks yet</h3>
          <p className="text-sm text-ink-secondary mt-1">Bookmark lessons and exercises to save them for later.</p>
        </div>
      )}
    </div>
  );
}
