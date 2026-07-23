"use client";

import Image from "next/image";
import Link from "next/link";
import { BookOpen, Clock } from "lucide-react";
import { Course } from "@/lib/api";

const difficultyColors: Record<string, string> = {
  beginner: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  intermediate: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
  advanced: "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300",
};

function formatDuration(minutes: number) {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.round(minutes / 60);
  return `${hours}h`;
}

interface CourseCardProps {
  course: Course;
  progressPercent?: number;
}

export function CourseCard({ course, progressPercent }: CourseCardProps) {
  return (
    <Link
      href={`/courses/${course.id}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white transition hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-700 dark:bg-slate-900"
    >
      <div className="relative h-48 overflow-hidden">
        <Image
          src={course.thumbnail ?? "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop"}
          alt={course.title}
          fill
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          className="object-cover transition duration-300 group-hover:scale-105"
        />
        <div className="absolute left-3 top-3">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              difficultyColors[course.difficulty] ??
              "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
            }`}
          >
            {course.difficulty}
          </span>
        </div>
      </div>
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-2 flex flex-wrap items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
          <span className="rounded-md bg-slate-100 px-2 py-0.5 dark:bg-slate-800">
            {course.programming_language}
          </span>
          {course.category && (
            <span className="rounded-md bg-slate-100 px-2 py-0.5 dark:bg-slate-800">
              {course.category}
            </span>
          )}
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
          {course.title}
        </h3>
        <p className="mt-2 line-clamp-2 flex-1 text-sm text-slate-600 dark:text-slate-400">
          {course.description}
        </p>
        <div className="mt-4 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            <span>{formatDuration(course.estimated_duration)}</span>
          </div>
          <div className="flex items-center gap-1">
            <BookOpen className="h-3.5 w-3.5" />
            <span>{course.skills.length} skills</span>
          </div>
        </div>
        {progressPercent !== undefined && progressPercent > 0 && (
          <div className="mt-4">
            <div className="h-1.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="h-full rounded-full bg-blue-600 transition-all"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="mt-1 text-xs font-medium text-slate-600 dark:text-slate-400">
              {progressPercent}% complete
            </p>
          </div>
        )}
      </div>
    </Link>
  );
}
