"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { courses as coursesApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { formatDuration, formatNumber, difficultyColor } from "@/lib/utils";
import type { CourseListItem } from "@/lib/types";
import {
  Search, Star, BookOpen, Clock, Users,
  TrendingUp, AlertCircle, RefreshCw,
} from "lucide-react";

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [sort, setSort] = useState("popular");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["courses", search, difficulty, sort],
    queryFn: () =>
      coursesApi.list({
        ...(search && { search }),
        ...(difficulty && { difficulty }),
        sort,
      }),
  });

  const items: CourseListItem[] = (data as any)?.items ?? [];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[#1a1d2e] dark:text-white">Explore Courses</h1>
        <p className="text-[#6b7280] dark:text-[#8b8fa3] mt-1">Discover courses and start your learning journey.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <Input
            placeholder="Search courses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="h-4 w-4" />}
          />
        </div>
        <div className="flex gap-2">
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="h-10 px-3 rounded-xl border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-[#1a1d2e] dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="h-10 px-3 rounded-xl border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-[#1a1d2e] dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="popular">Most Popular</option>
            <option value="newest">Newest</option>
            <option value="rating">Highest Rated</option>
          </select>
        </div>
      </div>

      {/* Featured Row */}
      <FeaturedCourses />

      {/* Error state */}
      {error && (
        <div className="rounded-2xl border border-red-200 dark:border-red-500/20 bg-red-50 dark:bg-red-500/5 p-6 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-red-700 dark:text-red-400">Failed to load courses</p>
            <p className="text-sm text-red-600/80 dark:text-red-400/80">Could not connect to the server. Please check your connection.</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} leftIcon={<RefreshCw className="h-4 w-4" />}>
            Retry
          </Button>
        </div>
      )}

      {/* Course Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : items.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`}>
              <Card hover padding="none" className="overflow-hidden h-full group">
                <div className="h-40 bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_30%,_rgba(255,255,255,0.1)_0%,_transparent_50%)]" />
                  <BookOpen className="h-10 w-10 text-white/30" />
                </div>
                <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <Badge size="sm" className={difficultyColor(course.difficulty)}>
                      {course.difficulty}
                    </Badge>
                    <div className="flex items-center gap-1 text-amber-500">
                      <Star className="h-3.5 w-3.5 fill-current" />
                      <span className="text-xs font-medium text-[#6b7280] dark:text-[#8b8fa3]">
                        {course.rating_average}
                        <span className="text-[#9ca3af] dark:text-[#6b7280] ml-0.5">({formatNumber(course.rating_count)})</span>
                      </span>
                    </div>
                  </div>
                  <h3 className="font-semibold text-[#1a1d2e] dark:text-white mb-1 line-clamp-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{course.title}</h3>
                  <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] line-clamp-2 mb-3">{course.description}</p>
                  <div className="flex items-center gap-3 text-xs text-[#9ca3af] dark:text-[#6b7280]">
                    <span className="flex items-center gap-1">
                      <BookOpen className="h-3 w-3" /> {course.lesson_count} lessons
                    </span>
                    {course.estimated_duration_minutes && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {formatDuration(course.estimated_duration_minutes)}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" /> {formatNumber(course.enrollment_count)}
                    </span>
                  </div>
                  {course.skill_tags && course.skill_tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {course.skill_tags.slice(0, 4).map((tag) => (
                        <Badge key={tag} size="sm" variant="outline">{tag}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : !error ? (
        <div className="text-center py-16">
          <BookOpen className="h-12 w-12 text-[#9ca3af] dark:text-[#6b7280] mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[#1a1d2e] dark:text-white">No courses found</h3>
          <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] mt-1">Try adjusting your search or filters.</p>
        </div>
      ) : null}
    </div>
  );
}

function FeaturedCourses() {
  const { data, isLoading } = useQuery({
    queryKey: ["featured-courses"],
    queryFn: () => coursesApi.getFeatured(),
  });

  // Safe access
  const items: CourseListItem[] = Array.isArray(data) ? data : [];

  if (isLoading || items.length === 0) return null;

  return (
    <div>
      <h2 className="text-lg font-semibold text-[#1a1d2e] dark:text-white mb-3 flex items-center gap-2">
        <TrendingUp className="h-5 w-5 text-brand-600 dark:text-brand-400" />
        Featured Courses
      </h2>
      <div className="grid md:grid-cols-3 gap-4">
        {items.slice(0, 3).map((course) => (
          <Link key={course.id} href={`/courses/${course.slug}`}>
            <Card hover padding="md" className="border-brand-100 dark:border-brand-500/20 bg-brand-50/30 dark:bg-brand-500/5">
              <Badge size="sm" className={difficultyColor(course.difficulty)}>
                {course.difficulty}
              </Badge>
              <h3 className="font-semibold text-[#1a1d2e] dark:text-white mt-2 line-clamp-2">{course.title}</h3>
              <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] mt-1 line-clamp-2">{course.description}</p>
              <div className="flex items-center gap-3 mt-3 text-xs text-[#9ca3af] dark:text-[#6b7280]">
                <span className="flex items-center gap-1">
                  <Star className="h-3 w-3 text-amber-500 fill-amber-500" /> {course.rating_average}
                </span>
                <span>{formatNumber(course.enrollment_count)} enrolled</span>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
