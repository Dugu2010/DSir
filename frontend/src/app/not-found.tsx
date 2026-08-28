"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Home, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center max-w-md">
        <div className="text-7xl font-display font-bold text-coral-500 dark:text-coral-400 mb-4">404</div>
        <p className="eyebrow mb-2">Lost in the archive</p>
        <h1 className="font-display text-2xl font-semibold text-ink mb-2">Page not found</h1>
        <p className="text-ink-secondary mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/">
            <Button variant="outline" leftIcon={<Home className="h-4 w-4" />}>
              Home
            </Button>
          </Link>
          <Link href="/courses">
            <Button leftIcon={<Search className="h-4 w-4" />}>
              Browse Courses
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
