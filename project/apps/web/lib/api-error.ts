import { AxiosError } from "axios";

export interface DetailedError {
  message: string;
  technical?: string;
  status?: number;
  url?: string;
  method?: string;
}

interface ErrorDetailItem {
  loc?: string[];
  msg?: string;
  type?: string;
}

interface BackendErrorData {
  detail?: string | ErrorDetailItem[];
  message?: string;
}

function getBackendMessage(err: AxiosError<BackendErrorData>): string | undefined {
  const data = err.response?.data;
  if (!data) return undefined;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((d) => (typeof d.msg === "string" ? d.msg : JSON.stringify(d)))
      .join("; ");
  }
  if (typeof data.message === "string") return data.message;
  return undefined;
}

export function parseApiError(err: unknown): DetailedError {
  if (err instanceof AxiosError || (err && typeof err === "object" && "isAxiosError" in err && (err as any).isAxiosError)) {
    const axiosErr = err as AxiosError<any>;
    const status = axiosErr.response?.status;
    const rawUrl = axiosErr.config?.url ?? axiosErr.response?.config?.url;
    const method = (axiosErr.config?.method ?? axiosErr.response?.config?.method)?.toUpperCase();
    // Strip query strings and hashes so tokens/secrets are not exposed in UI.
    const url = rawUrl ? rawUrl.split("?")[0].split("#")[0] : undefined;

    if (axiosErr.code === "ECONNABORTED" || axiosErr.code === "ETIMEDOUT") {
      return {
        message: "The request timed out. Please check your connection and try again.",
        technical: `Timeout: ${method || "REQUEST"} ${url || "unknown"}`,
        status,
        url,
        method,
      };
    }

    if (!axiosErr.response) {
      return {
        message: "Network error. Could not reach the server. Please check your internet connection.",
        technical: `Network error: ${method || "REQUEST"} ${url || "unknown"}`,
        status,
        url,
        method,
      };
    }

    const backend = getBackendMessage(axiosErr);

    if (status && status >= 500) {
      return {
        message: backend || "Something went wrong on our side. Please try again later.",
        technical: `Server error ${status}: ${method || "REQUEST"} ${url || "unknown"}`,
        status,
        url,
        method,
      };
    }

    if (status && status >= 400) {
      return {
        message: backend || "We couldn't complete your request. Please check your input and try again.",
        technical: `Client error ${status}: ${method || "REQUEST"} ${url || "unknown"}`,
        status,
        url,
        method,
      };
    }

    return {
      message: backend || "An unexpected error occurred.",
      technical: `HTTP ${status ?? "unknown"}: ${method || "REQUEST"} ${url || "unknown"}`,
      status,
      url,
      method,
    };
  }

  if (err instanceof Error) {
    return { message: err.message || "An unexpected error occurred." };
  }

  if (typeof err === "string") {
    return { message: err || "An unexpected error occurred." };
  }

  return { message: "An unexpected error occurred." };
}
