import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline" | "coral";
  size?: "sm" | "md";
  className?: string;
}

// Obsidian badges: mono, uppercase, outlined chips with calm tints.
const variantStyles = {
  default: "bg-surface-tertiary text-ink-secondary",
  success: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20",
  warning: "bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20",
  danger: "bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/20",
  info: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/20",
  coral: "bg-coral-500/10 text-coral-700 dark:text-coral-400 border border-coral-500/30",
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
        "inline-flex items-center font-mono font-medium uppercase tracking-wide rounded-full",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
