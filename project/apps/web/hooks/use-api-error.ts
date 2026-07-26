import { useState, useCallback } from "react";
import { parseApiError, DetailedError } from "@/lib/api-error";

interface UseApiErrorResult {
  error: string | null;
  details: string | null;
  setError: (err: unknown) => void;
  reset: () => void;
}

export function useApiError(): UseApiErrorResult {
  const [detailed, setDetailed] = useState<DetailedError | null>(null);

  const setError = useCallback((err: unknown) => {
    const parsed = parseApiError(err);
    setDetailed(parsed);
  }, []);

  const reset = useCallback(() => setDetailed(null), []);

  return {
    error: detailed?.message ?? null,
    details: detailed?.technical ?? null,
    setError,
    reset,
  };
}
