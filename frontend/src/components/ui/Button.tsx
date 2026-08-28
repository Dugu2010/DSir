"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

// Editorial button variants. Primary = coral with deep-navy text (WCAG AA).
const variants = {
  primary:
    "bg-coral-500 text-ink-inverse hover:bg-coral-600 active:bg-coral-700 dark:text-night-600 shadow-sm",
  secondary:
    "bg-surface text-ink hover:bg-surface-tertiary border border-border",
  outline:
    "border-2 border-coral-500 text-coral-700 dark:text-coral-400 hover:bg-coral-50 dark:hover:bg-coral-500/10",
  ghost: "text-ink-secondary hover:text-ink hover:bg-surface-tertiary",
  danger: "bg-red-600 text-white hover:bg-red-700 active:bg-red-800",
  success: "bg-emerald-600 text-white hover:bg-emerald-700",
};

const sizes = {
  sm: "h-8 px-3 text-sm gap-1.5 rounded-lg",
  md: "h-10 px-4 text-sm gap-2 rounded-xl",
  lg: "h-12 px-6 text-base gap-2 rounded-xl",
  xl: "h-14 px-8 text-base gap-2.5 rounded-2xl",
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
