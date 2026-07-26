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
        "rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-sm text-destructive",
        className
      )}
      aria-live="polite"
    >
      <div className="font-medium">{children}</div>
      {details && (
        <details className="mt-2">
          <summary className="cursor-pointer text-xs opacity-80">
            Technical details
          </summary>
          <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg bg-destructive/10 p-2 text-xs">
            {details}
          </pre>
        </details>
      )}
    </div>
  );
}
