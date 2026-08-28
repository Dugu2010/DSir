import { cn } from "@/lib/utils";
import { Loader2, AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn("animate-spin text-coral-500", className)} aria-hidden="true" />;
}

export function PageLoader({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex flex-col items-center gap-4" role="status" aria-live="polite">
        <Spinner className="h-8 w-8" />
        <p className="text-sm font-mono text-ink-tertiary">{label}</p>
      </div>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  icon,
  action,
}: {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-ink-tertiary mb-4">{icon}</div>}
      <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>
      {description && <p className="text-sm text-ink-secondary mt-1 max-w-md">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description = "We couldn't load this content. Please try again.",
  onRetry,
  className,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 text-center", className)}>
      <div className="h-14 w-14 rounded-2xl bg-red-50 dark:bg-red-500/10 flex items-center justify-center mb-4">
        <AlertTriangle className="h-7 w-7 text-red-500 dark:text-red-400" aria-hidden="true" />
      </div>
      <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>
      <p className="text-sm text-ink-secondary mt-1 max-w-md">{description}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} leftIcon={<RefreshCw className="h-3.5 w-3.5" />} className="mt-4">
          Try Again
        </Button>
      )}
    </div>
  );
}
