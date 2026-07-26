"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchRoadmap, fetchRoadmapCourses } from "@/lib/api";

export default function RoadmapDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: roadmap, isLoading: roadmapLoading } = useQuery({
    queryKey: ["roadmap", id],
    queryFn: () => fetchRoadmap(id),
  });

  const { data: coursesData, isLoading: coursesLoading } = useQuery({
    queryKey: ["roadmap-courses", id],
    queryFn: () => fetchRoadmapCourses(id),
  });

  if (roadmapLoading || !roadmap) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-1/2 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
        <div className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">{roadmap.title}</h1>
        <p className="mt-2 max-w-3xl text-muted-foreground">{roadmap.description}</p>
      </div>

      <section className="rounded-2xl border border-border bg-card p-6">
        <h2 className="text-xl font-bold text-card-foreground">Courses in this Roadmap</h2>
        {coursesLoading ? (
          <div className="mt-4 space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        ) : coursesData?.items.length ? (
          <ul className="mt-4 space-y-3">
            {coursesData.items.map((course, index) => (
              <li
                key={course.id}
                className="flex items-center justify-between rounded-xl border border-border bg-background p-4"
              >
                <div className="flex items-center gap-4">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                    {index + 1}
                  </span>
                  <div>
                    <h3 className="font-semibold text-card-foreground">{course.title}</h3>
                    <p className="text-sm text-muted-foreground">{course.programming_language ?? course.technology}</p>
                  </div>
                </div>
                <Link
                  href={`/courses/${course.id}`}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
                >
                  View
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-muted-foreground">No courses in this roadmap yet.</p>
        )}
      </section>
    </div>
  );
}
