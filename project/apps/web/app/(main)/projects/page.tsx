"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchCourses } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { FolderCode } from "lucide-react";

export default function ProjectsPage() {
  const { data: courses, isLoading, error, refetch } = useQuery({
    queryKey: ["courses"],
    queryFn: () => fetchCourses(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Projects</h1>
        <p className="text-muted-foreground">Apply what you learn with hands-on projects.</p>
      </div>

      {error && (
        <ErrorMessage>
          Failed to load projects.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-2xl bg-muted" />
          ))}
        </div>
      ) : courses?.items && courses.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.items.map((course) => (
            <Link
              key={course.id}
              href={`/projects/${course.id}`}
              className="group flex flex-col rounded-2xl border border-border bg-card p-6 transition hover:shadow-card"
            >
              <span className="w-fit rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                {course.programming_language ?? course.technology}
              </span>
              <h3 className="mt-4 text-lg font-bold text-card-foreground group-hover:text-primary">{course.title}</h3>
              <p className="mt-2 line-clamp-2 flex-1 text-sm text-muted-foreground">
                {course.description}
              </p>
              <span className="mt-4 text-sm font-semibold text-primary">View projects →</span>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<FolderCode className="h-6 w-6" />}
          title="No projects yet"
          description="Projects for each course will appear here as the content library grows."
          href="/courses"
          hrefLabel="Browse courses"
        />
      )}
    </div>
  );
}
