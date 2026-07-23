"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, Filter, Search, Sparkles } from "lucide-react";
import { fetchCourses } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CourseCard } from "@/components/course-card";

const categories = ["All", "Frontend", "Backend", "Full Stack"];
const languages = ["All", "Python", "JavaScript", "TypeScript", "HTML/CSS"];
const difficulties = ["All", "Beginner", "Intermediate", "Advanced"];
const sortOptions = [
  { value: "title", label: "Title" },
  { value: "estimated_duration", label: "Duration" },
  { value: "difficulty", label: "Difficulty" },
  { value: "created_at", label: "Newest" },
];

const tabs = [
  { name: "Browse", href: "/courses" },
  { name: "Completed", href: "/courses/completed" },
  { name: "Recently Viewed", href: "/courses/recently-viewed" },
  { name: "Bookmarks", href: "/courses/bookmarks" },
];

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [language, setLanguage] = useState("All");
  const [difficulty, setDifficulty] = useState("All");
  const [sort, setSort] = useState("title");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const pathname = usePathname();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["courses", search, category, language, difficulty, sort, sortOrder],
    queryFn: () =>
      fetchCourses({
        search: search.trim() || undefined,
        category: category === "All" ? undefined : category,
        programming_language: language === "All" ? undefined : language,
        difficulty: difficulty === "All" ? undefined : difficulty,
        sort,
        order: sortOrder,
      }),
  });

  const courses = data?.items ?? [];

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const isActive = pathname === tab.href;
          return (
            <Link
              key={tab.name}
              href={tab.href}
              className={cn(
                "whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition",
                isActive
                  ? "bg-blue-600 text-white"
                  : "bg-white text-slate-700 hover:bg-slate-100 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
              )}
            >
              {tab.name}
            </Link>
          );
        })}
      </div>

      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 to-violet-600 px-6 py-12 text-white sm:px-12 sm:py-16">
        <div className="relative z-10 max-w-2xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-sm font-medium backdrop-blur-sm">
            <Sparkles className="h-4 w-4" />
            <span>Start your learning journey</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Explore our courses
          </h1>
          <p className="mt-4 text-lg text-blue-100">
            Master programming with hands-on courses, interactive lessons, and AI-powered mentorship.
          </p>
        </div>
        <div className="absolute right-0 top-0 -translate-y-1/4 translate-x-1/4 opacity-20">
          <BookOpen className="h-96 w-96" />
        </div>
      </div>

      {/* Filters */}
      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <label htmlFor="course-search" className="sr-only">
              Search courses
            </label>
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              id="course-search"
              type="text"
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <label htmlFor="category-filter" className="sr-only">
              Category
            </label>
            <select
              id="category-filter"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c === "All" ? "All Categories" : c}
                </option>
              ))}
            </select>
            <label htmlFor="language-filter" className="sr-only">
              Language
            </label>
            <select
              id="language-filter"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            >
              {languages.map((l) => (
                <option key={l} value={l}>
                  {l === "All" ? "All Languages" : l}
                </option>
              ))}
            </select>
            <label htmlFor="difficulty-filter" className="sr-only">
              Difficulty
            </label>
            <select
              id="difficulty-filter"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            >
              {difficulties.map((d) => (
                <option key={d} value={d}>
                  {d === "All" ? "All Levels" : d}
                </option>
              ))}
            </select>
            <label htmlFor="sort-filter" className="sr-only">
              Sort
            </label>
            <select
              id="sort-filter"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            >
              {sortOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  Sort: {o.label}
                </option>
              ))}
            </select>
            <Button
              variant="secondary"
              onClick={() => setSortOrder((o) => (o === "asc" ? "desc" : "asc"))}
              className="shrink-0"
            >
              {sortOrder === "asc" ? "↑" : "↓"}
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <ErrorMessage>
          Failed to load courses.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      {/* Course Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
            >
              <Skeleton className="h-48 w-full rounded-none" />
              <div className="p-5">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="mt-3 h-4 w-full" />
                <Skeleton className="mt-2 h-4 w-2/3" />
              </div>
            </div>
          ))}
        </div>
      ) : courses.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 py-16 dark:border-slate-700">
          <Filter className="h-12 w-12 text-slate-400" />
          <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">
            No courses found
          </h3>
          <p className="mt-2 max-w-md text-center text-slate-600 dark:text-slate-400">
            Try adjusting your filters or search query to find what you&apos;re looking for.
          </p>
          <Button
            onClick={() => {
              setSearch("");
              setCategory("All");
              setLanguage("All");
              setDifficulty("All");
            }}
            variant="secondary"
            className="mt-4"
          >
            Clear filters
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}
