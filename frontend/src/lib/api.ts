// ── API Client for DSir ──

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
}

class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = "ApiError";
  }
}

async function request<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, auth = true } = options;

  const config: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  };

  if (auth && typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      (config.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }
  }

  if (body) {
    config.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, config);

  if (res.status === 401 && auth && typeof window !== "undefined") {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const retryConfig = { ...config };
      const token = localStorage.getItem("access_token");
      if (token) {
        (retryConfig.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
      }
      const retryRes = await fetch(`${API_BASE}${endpoint}`, retryConfig);
      if (!retryRes.ok) {
        const error = await retryRes.json().catch(() => ({ detail: "Request failed" }));
        throw new ApiError(retryRes.status, error.detail || "Request failed");
      }
      return retryRes.json();
    }
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(res.status, error.detail || "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

async function tryRefreshToken(): Promise<boolean> {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;
    const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return false;
    }
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// ── Auth ──

export const auth = {
  signup: (data: { email: string; username: string; display_name: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/signup", {
      method: "POST", body: data, auth: false,
    }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/login", {
      method: "POST", body: data, auth: false,
    }),
  logout: () => request("/api/v1/auth/logout", { method: "POST" }),
  me: () => request<import("./types").User>("/api/v1/auth/me"),
  refresh: (refresh_token: string) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/refresh", {
      method: "POST", body: { refresh_token }, auth: false,
    }),
};

// ── Users ──

export const users = {
  getDashboard: () => request<import("./types").Dashboard>("/api/v1/users/me/dashboard"),
  getStats: () => request<import("./types").UserStats>("/api/v1/users/me/stats"),
  getEnrollments: () => request<import("./types").Enrollment[]>("/api/v1/users/me/enrollments"),
  enroll: (courseId: string) => request(`/api/v1/users/me/enrollments/${courseId}`, { method: "POST" }),
  updateProfile: (data: Partial<import("./types").User>) =>
    request<import("./types").User>("/api/v1/users/me", { method: "PATCH", body: data }),
  getBookmarks: () => request("/api/v1/users/me/bookmarks"),
  createBookmark: (data: { lesson_id?: string; exercise_id?: string; note?: string }) =>
    request("/api/v1/users/me/bookmarks", { method: "POST", body: data }),
  deleteBookmark: (id: string) => request(`/api/v1/users/me/bookmarks/${id}`, { method: "DELETE" }),
  getNotes: (lessonId?: string) =>
    request(`/api/v1/users/me/notes${lessonId ? `?lesson_id=${lessonId}` : ""}`),
  createNote: (data: { lesson_id: string; content: string }) =>
    request("/api/v1/users/me/notes", { method: "POST", body: data }),
  getNotifications: (page = 1, unreadOnly = false) =>
    request(`/api/v1/users/me/notifications?page=${page}&size=20${unreadOnly ? "&unread_only=true" : ""}`),
};

// ── Courses ──

export const courses = {
  list: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").CourseListItem>>(`/api/v1/courses/?${qs}`, { auth: false });
  },
  get: (slug: string) => request<import("./types").Course>(`/api/v1/courses/${slug}`),
  getFeatured: () => request<import("./types").CourseListItem[]>("/api/v1/courses/featured", { auth: false }),
  getModules: (slug: string) => request<import("./types").Module[]>(`/api/v1/courses/${slug}/modules`),
  getLessons: (slug: string) => request(`/api/v1/courses/${slug}/lessons`),
};

// ── Learning ──

export const learning = {
  getLesson: (courseSlug: string, moduleSlug: string, lessonSlug: string) =>
    request<import("./types").Lesson>(`/api/v1/learn/${courseSlug}/${moduleSlug}/${lessonSlug}`),
  getProgress: (courseSlug: string, moduleSlug: string, lessonSlug: string) =>
    request(`/api/v1/learn/${courseSlug}/${moduleSlug}/${lessonSlug}/progress`),
  updateProgress: (courseSlug: string, moduleSlug: string, lessonSlug: string, data: Record<string, unknown>) =>
    request(`/api/v1/learn/${courseSlug}/${moduleSlug}/${lessonSlug}/progress`, { method: "PUT", body: data }),
  getRecentlyViewed: () => request("/api/v1/learn/me/recently-viewed"),
  getExercises: (courseSlug: string, moduleSlug: string, lessonSlug: string) =>
    request<import("./types").Exercise[]>(`/api/v1/learn/${courseSlug}/${moduleSlug}/${lessonSlug}/exercises`),
};

// ── Practice ──

export const practice = {
  listExercises: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").Exercise>>(`/api/v1/practice/exercises?${qs}`);
  },
  getExercise: (id: string) => request(`/api/v1/practice/exercises/${id}`),
  submit: (exerciseId: string, code: string, language: string) =>
    request<import("./types").Submission>(`/api/v1/practice/exercises/${exerciseId}/submit`, {
      method: "POST", body: { code, language },
    }),
  getSubmissions: (page = 1, exerciseId?: string) =>
    request(`/api/v1/practice/submissions?page=${page}&size=20${exerciseId ? `&exercise_id=${exerciseId}` : ""}`),
};

// ── Revision ──

export const revision = {
  getFlashcards: (page = 1) =>
    request<import("./types").PaginatedResponse<import("./types").Flashcard>>(`/api/v1/revision/flashcards?page=${page}&size=50`),
  getDueFlashcards: () => request<import("./types").Flashcard[]>("/api/v1/revision/flashcards/due?limit=20"),
  createFlashcard: (data: { front_content: string; back_content: string; lesson_id?: string }) =>
    request("/api/v1/revision/flashcards", { method: "POST", body: data }),
  reviewFlashcard: (cardId: string, quality: number) =>
    request(`/api/v1/revision/flashcards/${cardId}/review`, { method: "POST", body: { quality } }),
  getStats: () => request("/api/v1/revision/stats"),
};

// ── AI ──

export const ai = {
  getConversations: () => request<import("./types").AIConversation[]>("/api/v1/ai/conversations"),
  createConversation: (data: { assistant_type: string; title?: string }) =>
    request<import("./types").AIConversation>("/api/v1/ai/conversations", { method: "POST", body: data }),
  getMessages: (convId: string) => request<import("./types").AIMessage[]>(`/api/v1/ai/conversations/${convId}/messages`),
  sendMessage: (convId: string, content: string) =>
    request<import("./types").AIMessage>(`/api/v1/ai/conversations/${convId}/messages`, {
      method: "POST", body: { content },
    }),
  deleteConversation: (convId: string) =>
    request(`/api/v1/ai/conversations/${convId}`, { method: "DELETE" }),
};

// ── Admin ──

export const admin = {
  getDashboard: () => request("/api/v1/admin/dashboard"),
  getUsers: (page = 1) => request(`/api/v1/admin/users?page=${page}&size=20`),
  getCourses: (page = 1) => request(`/api/v1/admin/courses?page=${page}&size=20`),
};

export { ApiError };

// ── Generic API client (used by auth-store and learn/practice pages) ──

export const api = {
  get: <T = any>(endpoint: string) => request<T>(endpoint),
  post: <T = any>(endpoint: string, body?: unknown) => request<T>(endpoint, { method: "POST", body }),
  put: <T = any>(endpoint: string, body?: unknown) => request<T>(endpoint, { method: "PUT", body }),
  patch: <T = any>(endpoint: string, body?: unknown) => request<T>(endpoint, { method: "PATCH", body }),
  delete: <T = any>(endpoint: string) => request<T>(endpoint, { method: "DELETE" }),
};
