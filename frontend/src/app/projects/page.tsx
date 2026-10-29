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
  const capstones = items.filter((p) => p.is_capstone).length;
  const totalHours = items.reduce((sum, p) => sum + (p.estimated_duration_hours || 0), 0);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8">
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 16 · Applied engineering
          </p>
          <h1 className="font-display text-3xl md:text-5xl font-medium tracking-tight leading-[1.08] text-ink mt-3">
            Build &amp; Apply{" "}
            <span className="italic text-coral-600 dark:text-coral-400">Projects.</span>
          </h1>
          <p className="text-ink-secondary mt-3 max-w-2xl">
            Apply what you&apos;ve learned by building real projects.
          </p>
        </div>
        {items.length > 0 && (
          <dl className="grid grid-cols-3 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
            {[
              { label: "Projects", value: items.length },
              { label: "Capstones", value: capstones },
              { label: "Estimated hours", value: totalHours || "—" },
            ].map((stat) => (
              <div key={stat.label} className="bg-surface dark:bg-night-500 px-5 py-4">
                <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">{stat.label}</dt>
                <dd className="font-display text-2xl font-medium text-ink mt-1 tabular-nums">{stat.value}</dd>
              </div>
            ))}
          </dl>
        )}
      </header>

      {items.length === 0 ? (
        <EmptyState title="No projects yet" description="Projects will appear here once they're published." icon={<FolderKanban className="h-8 w-8" />} />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {items.map((p, index) => (
            <Link key={p.id} href={`/projects/${p.id}`} className="group block">
              <Card hover padding="md" className="h-full flex flex-col">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400">
                    Project // {String(index + 1).padStart(2, "0")}
                  </span>
                  <Badge size="sm" className={difficultyColor(p.difficulty)}>{p.difficulty}</Badge>
                </div>
                <h3 className="font-display text-lg font-medium text-ink mb-1 group-hover:text-coral-700 dark:group-hover:text-coral-400 transition-colors">
                  {p.title}
                </h3>
                <p className="text-sm text-ink-secondary line-clamp-2 mb-4">{p.description}</p>
                <div className="mt-auto pt-3 border-t border-border dark:border-white/10 flex flex-wrap items-center gap-x-4 gap-y-2 font-mono text-[10px] uppercase tracking-[0.12em] text-ink-tertiary">
                  {p.is_capstone && (
                    <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                      <Star className="h-3.5 w-3.5 fill-current" /> Capstone
                    </span>
                  )}
                  {p.estimated_duration_hours && (
                    <span className="flex items-center gap-1 tabular-nums">
                      <Clock className="h-3.5 w-3.5" /> ~{p.estimated_duration_hours}h
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-coral-600 dark:text-coral-400 ml-auto group-hover:gap-2 transition-all">
                    Open <ChevronRight className="h-3.5 w-3.5" />
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
