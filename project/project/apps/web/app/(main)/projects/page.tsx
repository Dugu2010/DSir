"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchCourses } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

export default function ProjectsPage() {
  const { data: courses, isLoading, error, refetch } = useQuery({
    queryKey: ["courses"],
    queryFn: () => fetchCourses(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Projects</h1>
        <p className="text-slate-600 dark:text-slate-400">Apply what you learn with hands-on projects.</p>
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
            <div key={i} className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses?.items.map((course) => (
            <Link
              key={course.id}
              href={`/projects/${course.id}`}
              className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
            >
              <span className="w-fit rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                {course.technology}
              </span>
              <h3 className="mt-4 text-lg font-bold text-slate-900 dark:text-white">{course.title}</h3>
              <p className="mt-2 line-clamp-2 flex-1 text-sm text-slate-600 dark:text-slate-400">
                {course.description}
              </p>
              <span className="mt-4 text-sm font-semibold text-blue-600 dark:text-blue-400">View projects →</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
