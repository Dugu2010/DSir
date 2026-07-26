import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  href?: string;
  hrefLabel?: string;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  href,
  hrefLabel,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card/50 p-8 text-center",
        className
      )}
    >
      {icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-card-foreground">{title}</h3>
      {description && (
        <p className="mt-2 max-w-md text-sm text-muted-foreground">{description}</p>
      )}
      {action && (
        <Button onClick={action.onClick} className="mt-6">
          {action.label}
        </Button>
      )}
      {href && (
        <Link
          href={href}
          className="mt-6 inline-flex h-10 items-center justify-center rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
        >
          {hrefLabel ?? "Get started"}
        </Link>
      )}
    </div>
  );
}
