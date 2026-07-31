import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
}

export function Skeleton({ className, variant = "rectangular" }: SkeletonProps) {
  const base = "animate-shimmer bg-gradient-to-r from-surface-tertiary via-surface-secondary to-surface-tertiary bg-[length:200%_100%]";

  const variants = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-xl",
  };

  return <div className={cn(base, variants[variant], className)} />;
}

export function CardSkeleton() {
  return (
    <div className="rounded-2xl border border-border p-6 space-y-4">
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-5 w-3/4" variant="text" />
      <Skeleton className="h-4 w-full" variant="text" />
      <Skeleton className="h-4 w-2/3" variant="text" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-16" />
      </div>
    </div>
  );
}
