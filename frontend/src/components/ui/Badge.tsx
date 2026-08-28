import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline" | "coral";
  size?: "sm" | "md";
  className?: string;
}

// Editorial badges: mono type, rounded-full, calm tints. `coral` is the
// accent badge used for "free", featured and highlighted states.
const variantStyles = {
  default: "bg-surface-tertiary text-ink-secondary dark:bg-white/5",
  success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-500/10 dark:text-amber-400",
  danger: "bg-red-100 text-red-800 dark:bg-red-500/10 dark:text-red-400",
  info: "bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400",
  coral: "bg-coral-50 text-coral-700 dark:bg-coral-500/10 dark:text-coral-400",
  outline: "border border-border text-ink-secondary",
};

const sizeStyles = {
  sm: "px-2 py-0.5 text-2xs",
  md: "px-2.5 py-1 text-xs",
};

export function Badge({ children, variant = "default", size = "md", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center font-mono font-medium rounded-full",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
