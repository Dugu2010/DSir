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
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{roadmap.title}</h1>
        <p className="mt-2 max-w-3xl text-slate-600 dark:text-slate-400">{roadmap.description}</p>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Courses in this Roadmap</h2>
        {coursesLoading ? (
          <div className="mt-4 space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
            ))}
          </div>
        ) : coursesData?.items.length ? (
          <ul className="mt-4 space-y-3">
            {coursesData.items.map((course, index) => (
              <li
                key={course.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-center gap-4">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                    {index + 1}
                  </span>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">{course.title}</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{course.technology}</p>
                  </div>
                </div>
                <Link
                  href={`/courses/${course.id}`}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  View
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-slate-600 dark:text-slate-400">No courses in this roadmap yet.</p>
        )}
      </section>
    </div>
  );
}
