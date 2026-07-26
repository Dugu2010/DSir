"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchRoadmaps } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Map } from "lucide-react";

export default function RoadmapsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["roadmaps"],
    queryFn: fetchRoadmaps,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Learning Roadmaps</h1>
        <p className="text-muted-foreground">Structured paths to master new technologies.</p>
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
            <div key={i} className="h-40 animate-pulse rounded-2xl bg-muted" />
          ))}
        </div>
      ) : data?.items && data.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((roadmap) => (
            <Link
              key={roadmap.id}
              href={`/roadmaps/${roadmap.id}`}
              className="group flex flex-col rounded-2xl border border-border bg-card p-6 transition hover:shadow-card"
            >
              <h3 className="text-lg font-bold text-card-foreground group-hover:text-primary">{roadmap.title}</h3>
              <p className="mt-2 line-clamp-3 flex-1 text-sm text-muted-foreground">
                {roadmap.description}
              </p>
              <span className="mt-4 text-sm font-semibold text-primary">Explore →</span>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Map className="h-6 w-6" />}
          title="No roadmaps yet"
          description="Learning roadmaps will be added here to guide your journey."
          href="/courses"
          hrefLabel="Browse courses"
        />
      )}
    </div>
  );
}
