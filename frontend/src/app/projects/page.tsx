"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { projects } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { FolderKanban, ChevronRight, Clock, Star } from "lucide-react";
import { difficultyColor } from "@/lib/utils";

export default function ProjectsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projects.list(),
  });

  if (isLoading) return <PageLoader label="Loading projects..." />;
  if (error || !data) {
    return (
      <ErrorState title="Couldn't load projects" description="Check your connection and try again." onRetry={() => refetch()} />
    );
  }

  const items: any[] = data.items || [];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <p className="eyebrow mb-2">Build & Apply</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
          <FolderKanban className="h-8 w-8 text-coral-500" />
          Projects
        </h1>
        <p className="text-ink-secondary mt-1">
          Apply what you&apos;ve learned by building real projects.
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState title="No projects yet" description="Projects will appear here once they're published." icon={<FolderKanban className="h-8 w-8" />} />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {items.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card hover padding="md" className="h-full">
                <div className="flex items-start justify-between mb-3">
                  <Badge size="sm" className={difficultyColor(p.difficulty)}>{p.difficulty}</Badge>
                  {p.is_capstone && (
                    <span className="flex items-center gap-1 text-xs text-amber-500 font-medium">
                      <Star className="h-3.5 w-3.5 fill-current" /> Capstone
                    </span>
                  )}
                </div>
                <h3 className="font-display font-semibold text-ink mb-1">{p.title}</h3>
                <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{p.description}</p>
                <div className="flex items-center gap-4 text-xs text-ink-tertiary">
                  {p.estimated_duration_hours && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" /> ~{p.estimated_duration_hours}h
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-coral-600 dark:text-coral-400 font-medium ml-auto">
                    View project <ChevronRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
