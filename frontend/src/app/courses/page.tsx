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
  Search, Star, BookOpen, Clock, Users, Filter,
  TrendingUp, Grid3X3, List, SlidersHorizontal,
} from "lucide-react";

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [sort, setSort] = useState("popular");

  const { data, isLoading } = useQuery({
    queryKey: ["courses", search, difficulty, sort],
    queryFn: () =>
      coursesApi.list({
        ...(search && { search }),
        ...(difficulty && { difficulty }),
        sort,
      }),
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-ink">Explore Courses</h1>
        <p className="text-ink-secondary mt-1">Discover courses and start your learning journey.</p>
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
            className="h-10 px-3 rounded-xl border border-border bg-surface text-sm text-ink focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="h-10 px-3 rounded-xl border border-border bg-surface text-sm text-ink focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="popular">Most Popular</option>
            <option value="newest">Newest</option>
            <option value="rating">Highest Rated</option>
          </select>
        </div>
      </div>

      {/* Featured Row */}
      <FeaturedCourses />

      {/* Course Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.items.map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`}>
              <Card hover padding="none" className="overflow-hidden">
                {/* Course image placeholder */}
                <div className="h-40 bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                  <BookOpen className="h-10 w-10 text-white/40" />
                </div>
                <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <Badge size="sm" className={difficultyColor(course.difficulty)}>
                      {course.difficulty}
                    </Badge>
                    <div className="flex items-center gap-1 text-amber-500">
                      <Star className="h-3.5 w-3.5 fill-current" />
                      <span className="text-xs font-medium text-ink-secondary">
                        {course.rating_average}
                        <span className="text-ink-tertiary ml-0.5">({formatNumber(course.rating_count)})</span>
                      </span>
                    </div>
                  </div>
                  <h3 className="font-semibold text-ink mb-1 line-clamp-2">{course.title}</h3>
                  <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{course.description}</p>
                  <div className="flex items-center gap-3 text-xs text-ink-tertiary">
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
                        <Badge key={tag} size="sm" variant="outline">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <BookOpen className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-ink">No courses found</h3>
          <p className="text-sm text-ink-secondary mt-1">Try adjusting your search or filters.</p>
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          {Array.from({ length: data.pages }, (_, i) => (
            <Button
              key={i}
              variant={data.page === i + 1 ? "primary" : "ghost"}
              size="sm"
            >
              {i + 1}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}

function FeaturedCourses() {
  const { data, isLoading } = useQuery({
    queryKey: ["featured-courses"],
    queryFn: () => coursesApi.getFeatured(),
  });

  if (isLoading || !data || data.length === 0) return null;

  return (
    <div>
      <h2 className="text-lg font-semibold text-ink mb-3 flex items-center gap-2">
        <TrendingUp className="h-5 w-5 text-brand-600" />
        Featured Courses
      </h2>
      <div className="grid md:grid-cols-3 gap-4">
        {data.slice(0, 3).map((course) => (
          <Link key={course.id} href={`/courses/${course.slug}`}>
            <Card hover padding="md" className="border-brand-200 dark:border-brand-900 bg-brand-50/30 dark:bg-brand-950/10">
              <Badge size="sm" className={difficultyColor(course.difficulty)}>
                {course.difficulty}
              </Badge>
              <h3 className="font-semibold text-ink mt-2 line-clamp-2">{course.title}</h3>
              <p className="text-sm text-ink-secondary mt-1 line-clamp-2">{course.description}</p>
              <div className="flex items-center gap-3 mt-3 text-xs text-ink-tertiary">
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
