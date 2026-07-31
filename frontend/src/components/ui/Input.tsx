"use client";

import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { AlertCircle } from "lucide-react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, leftIcon, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-ink">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-tertiary">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              "w-full h-10 px-3 rounded-xl border bg-surface text-ink text-sm",
              "placeholder:text-ink-tertiary",
              "transition-all duration-150",
              "focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              leftIcon && "pl-10",
              error
                ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                : "border-border hover:border-ink-tertiary",
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="flex items-center gap-1 text-xs text-red-600">
            <AlertCircle className="h-3 w-3" />
            {error}
          </p>
        )}
        {hint && !error && (
          <p className="text-xs text-ink-tertiary">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
