import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  children: React.ReactNode;
  className?: string;
}

export function ErrorMessage({ children, className }: ErrorMessageProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-950 dark:text-red-200",
        className
      )}
    >
      {children}
    </div>
  );
}
