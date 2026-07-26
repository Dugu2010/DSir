import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  children: React.ReactNode;
  className?: string;
  details?: string | null;
}

export function ErrorMessage({ children, className, details }: ErrorMessageProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-950 dark:text-red-200",
        className
      )}
      aria-live="polite"
    >
      <div className="font-medium">{children}</div>
      {details && (
        <details className="mt-2">
          <summary className="cursor-pointer text-xs text-red-500 dark:text-red-300">
            Technical details
          </summary>
          <pre className="mt-2 whitespace-pre-wrap break-words rounded bg-red-100 p-2 text-xs text-red-700 dark:bg-red-900 dark:text-red-100">
            {details}
          </pre>
        </details>
      )}
    </div>
  );
}
