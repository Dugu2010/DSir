"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

// Obsidian Protocol buttons: pill geometry, coral primary with white text,
// flat secondary surfaces with low-contrast outlines.
const variants = {
  primary:
    "bg-coral-500 text-white hover:bg-coral-600 active:bg-coral-700 dark:text-white shadow-none",
  secondary:
    "bg-surface text-ink border border-border hover:bg-surface-tertiary hover:border-border-light",
  outline:
    "border border-coral-500/60 text-coral-700 dark:text-coral-400 hover:bg-coral-500/10 hover:border-coral-500",
  ghost: "text-ink-secondary hover:text-ink hover:bg-surface-tertiary",
  danger: "bg-red-600 text-white hover:bg-red-700 active:bg-red-800",
  success: "bg-emerald-600 text-white hover:bg-emerald-700",
};

const sizes = {
  sm: "h-9 px-3.5 text-sm gap-1.5 rounded-full",
  md: "h-10 px-4 text-sm gap-2 rounded-full",
  lg: "h-11 px-5 text-sm gap-2 rounded-full",
  xl: "h-12 px-6 text-base gap-2.5 rounded-full",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", loading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-all duration-150",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-secondary dark:focus-visible:ring-offset-night-600",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "active:scale-[0.98]",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : leftIcon}
        {children}
        {!loading && rightIcon}
      </button>
    );
  }
);

Button.displayName = "Button";
