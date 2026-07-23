"use client";

import { useQuery } from "@tanstack/react-query";
import { Bookmark } from "lucide-react";
import { fetchBookmarks } from "@/lib/api";
import { CourseCard } from "@/components/course-card";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";

export default function BookmarksPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: fetchBookmarks,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Bookmarked Courses</h1>
        <p className="text-slate-600 dark:text-slate-400">Your saved courses for later.</p>
      </div>

      {error && (
        <ErrorMessage>
          Failed to load bookmarks.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : data?.items.length ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((item) =>
            item.course ? <CourseCard key={item.id} course={item.course} /> : null
          )}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 py-16 dark:border-slate-700">
          <Bookmark className="h-12 w-12 text-slate-400" />
          <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">No bookmarks yet</h3>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Browse courses and bookmark the ones you want to learn later.
          </p>
          <Link
            href="/courses"
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            Browse courses
          </Link>
        </div>
      )}
    </div>
  );
}
