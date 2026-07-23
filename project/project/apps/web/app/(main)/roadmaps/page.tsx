"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchRoadmaps } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

export default function RoadmapsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["roadmaps"],
    queryFn: fetchRoadmaps,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Learning Roadmaps</h1>
        <p className="text-slate-600 dark:text-slate-400">Structured paths to master new technologies.</p>
      </div>

      {error && (
        <ErrorMessage>
          Failed to load roadmaps.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((roadmap) => (
            <Link
              key={roadmap.id}
              href={`/roadmaps/${roadmap.id}`}
              className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
            >
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">{roadmap.title}</h3>
              <p className="mt-2 line-clamp-3 flex-1 text-sm text-slate-600 dark:text-slate-400">
                {roadmap.description}
              </p>
              <span className="mt-4 text-sm font-semibold text-blue-600 dark:text-blue-400">Explore →</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
