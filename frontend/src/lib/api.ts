// API Client for DSir

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
    headers: { "Content-Type": "application/json", ...headers },
  };

  if (auth && typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) (config.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  if (body) config.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${endpoint}`, config);

  if (res.status === 401 && auth && typeof window !== "undefined") {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const retryConfig = { ...config };
      const token = localStorage.getItem("access_token");
      if (token) (retryConfig.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
      const retryRes = await fetch(`${API_BASE}${endpoint}`, retryConfig);
      if (!retryRes.ok) {
        const error = await retryRes.json().catch(() => ({}));
        throw new ApiError(retryRes.status, error.message || error.detail || "Request failed");
      }
      return retryRes.json();
    }
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new ApiError(res.status, error.message || error.detail || "Request failed");
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

// Auth

export const auth = {
  signup: (data: { email: string; username: string; display_name: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/signup", { method: "POST", body: data, auth: false }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/login", { method: "POST", body: data, auth: false }),
  logout: () => request("/api/v1/auth/logout", { method: "POST" }),
  me: () => request<import("./types").User>("/api/v1/auth/me"),
  refresh: (refresh_token: string) =>
    request<{ access_token: string; refresh_token: string }>("/api/v1/auth/refresh", { method: "POST", body: { refresh_token }, auth: false }),
  changePassword: (data: { current_password: string; new_password: string }) =>
    request("/api/v1/auth/change-password", { method: "POST", body: data }),
  forgotPassword: (email: string) =>
    request<{ detail: string; reset_token?: string; reset_link?: string }>("/api/v1/auth/forgot-password", { method: "POST", body: { email }, auth: false }),
  resetPassword: (token: string, new_password: string) =>
    request("/api/v1/auth/reset-password", { method: "POST", body: { token, new_password }, auth: false }),
  verifyEmail: (token: string) =>
    request("/api/v1/auth/verify-email", { method: "POST", body: {}, auth: false }),
  resendVerification: () =>
    request("/api/v1/auth/resend-verification", { method: "POST" }),
};

// Users

export const users = {
  getDashboard: () => request<import("./types").Dashboard>("/api/v1/users/me/dashboard"),
  getStats: () => request<import("./types").UserStats>("/api/v1/users/me/stats"),
  getEnrollments: () => request<import("./types").Enrollment[]>("/api/v1/users/me/enrollments"),
  enroll: (courseId: string) => request(`/api/v1/users/me/enrollments/${courseId}`, { method: "POST" }),
  getCertificates: () => request<import("./types").Certificate[]>("/api/v1/users/me/certificates"),
  updateProfile: (data: Partial<import("./types").User>) =>
    request<import("./types").User>("/api/v1/users/me", { method: "PATCH", body: data }),
  getBookmarks: () => request("/api/v1/users/me/bookmarks"),
  createBookmark: (data: { lesson_id?: string; exercise_id?: string; note?: string }) =>
    request("/api/v1/users/me/bookmarks", { method: "POST", body: data }),
  deleteBookmark: (id: string) => request(`/api/v1/users/me/bookmarks/${id}`, { method: "DELETE" }),
  getNotes: (lessonId?: string) => request<import("./types").UserNote[]>(`/api/v1/users/me/notes${lessonId ? `?lesson_id=${lessonId}` : ""}`),
  createNote: (data: { lesson_id: string; content: string }) =>
    request("/api/v1/users/me/notes", { method: "POST", body: data }),
  getNotifications: (page = 1, unreadOnly = false) =>
    request(`/api/v1/users/me/notifications?page=${page}&size=20${unreadOnly ? "&unread_only=true" : ""}`),
  markNotificationRead: (id: string) =>
    request(`/api/v1/users/me/notifications/${id}/read`, { method: "POST" }),
  markAllNotificationsRead: () => request(`/api/v1/users/me/notifications/read-all`, { method: "POST" }),
  updateDailyGoal: (data: { target_minutes: number; target_lessons: number; target_exercises: number }) =>
    request(`/api/v1/users/me/daily-goal`, { method: "PUT", body: data }),
  getKnowledge: () => request<import("./types").KnowledgeItem[]>("/api/v1/users/me/knowledge"),
  getAchievements: () => request<import("./types").Achievement[]>("/api/v1/users/me/achievements"),
};

// Courses

export const courses = {
  list: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").CourseListItem>>(`/api/v1/courses/?${qs}`, { auth: false });
  },
  get: (slug: string) => request<import("./types").Course>(`/api/v1/courses/${slug}`),
  getFeatured: () => request<import("./types").CourseListItem[]>("/api/v1/courses/featured", { auth: false }),
  getModules: (slug: string) => request<import("./types").Module[]>(`/api/v1/courses/${slug}/modules`),
  // Returns the full course structure (modules with their lessons). The
  // backend exposes this as /courses/{slug}/modules.
  getLessons: (slug: string) => request<import("./types").CourseStructure[]>(`/api/v1/courses/${slug}/modules`),
  getReviews: (slug: string) =>
    request<import("./types").PaginatedResponse<import("./types").Review>>(`/api/v1/courses/${slug}/reviews`, { auth: false }),
  createReview: (slug: string, data: { rating: number; review?: string }) =>
    request<import("./types").Review>(`/api/v1/courses/${slug}/reviews`, { method: "POST", body: data }),
  delete: (slug: string) => request(`/api/v1/courses/${slug}`, { method: "DELETE" }),
};

// Learning

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

// Practice

export const practice = {
  listExercises: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").Exercise>>(`/api/v1/practice/exercises?${qs}`);
  },
  getExercise: (id: string) => request(`/api/v1/practice/exercises/${id}`),
  submit: (exerciseId: string, code: string, language: string) =>
    request<import("./types").Submission>(`/api/v1/practice/exercises/${exerciseId}/submit`, { method: "POST", body: { code, language } }),
  getSubmissions: (page = 1, exerciseId?: string) =>
    request(`/api/v1/practice/submissions?page=${page}&size=20${exerciseId ? `&exercise_id=${exerciseId}` : ""}`),
};

// Revision

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

// AI

export const ai = {
  getConversations: () => request<import("./types").AIConversation[]>("/api/v1/ai/conversations"),
  createConversation: (data: { assistant_type: string; title?: string }) =>
    request<import("./types").AIConversation>("/api/v1/ai/conversations", { method: "POST", body: data }),
  getMessages: (convId: string) => request<import("./types").AIMessage[]>(`/api/v1/ai/conversations/${convId}/messages`),
  sendMessage: (convId: string, content: string) =>
    request<import("./types").AIMessage>(`/api/v1/ai/conversations/${convId}/messages`, { method: "POST", body: { content } }),
  deleteConversation: (convId: string) => request(`/api/v1/ai/conversations/${convId}`, { method: "DELETE" }),
};

// Quizzes

export const quizzes = {
  list: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").QuizListItem>>(`/api/v1/quizzes/?${qs}`);
  },
  getDetail: (quizId: string) =>
    request<import("./types").QuizDetail>(`/api/v1/quizzes/${quizId}`),
  submit: (quizId: string, answers: Record<string, unknown>) =>
    request<import("./types").QuizResult>(`/api/v1/quizzes/${quizId}/submit`, { method: "POST", body: { answers } }),
  getResults: (quizId: string) =>
    request<import("./types").QuizResult>(`/api/v1/quizzes/${quizId}/results`),
};

// Projects

export const projects = {
  list: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<any>>(`/api/v1/practice/projects?${qs}`);
  },
  get: (projectId: string) =>
    request<import("./types").ProjectDetail>(`/api/v1/practice/projects/${projectId}`),
  submit: (projectId: string, codeFiles: Record<string, unknown>) =>
    request<import("./types").ProjectSubmission>(`/api/v1/practice/projects/${projectId}/submit`, { method: "POST", body: { code_files: codeFiles } }),
  getSubmissions: (page = 1) =>
    request<import("./types").PaginatedResponse<import("./types").ProjectSubmission>>(`/api/v1/practice/projects/submissions?page=${page}&size=20`),
};

// Discussions

export const discussions = {
  list: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<import("./types").PaginatedResponse<import("./types").Discussion>>(`/api/v1/discussions?${qs}`);
  },
  create: (data: { title: string; content: string; lesson_id?: string }) =>
    request<import("./types").Discussion>(`/api/v1/discussions`, { method: "POST", body: data }),
  get: (discussionId: string) =>
    request<import("./types").Discussion>(`/api/v1/discussions/${discussionId}`),
  addReply: (discussionId: string, data: { content: string; parent_id?: string }) =>
    request<import("./types").DiscussionReply>(`/api/v1/discussions/${discussionId}/replies`, { method: "POST", body: data }),
  markSolution: (replyId: string) =>
    request(`/api/v1/discussions/replies/${replyId}/solution`, { method: "PUT" }),
  voteReply: (replyId: string, direction: "up" | "down") =>
    request(`/api/v1/discussions/replies/${replyId}/vote`, { method: "POST", body: { direction } }),
};

// Leaderboard

export const leaderboard = {
  get: (period: "daily" | "weekly" | "monthly" | "all_time" = "weekly") =>
    request<import("./types").LeaderboardEntry[]>(`/api/v1/leaderboard?period=${period}`),
  getMyRank: (period: "daily" | "weekly" | "monthly" | "all_time" = "weekly") =>
    request<import("./types").UserRank>(`/api/v1/leaderboard/me?period=${period}`),
};

// Admin

export const admin = {
  getDashboard: () => request("/api/v1/admin/dashboard"),
  getUsers: (page = 1) => request(`/api/v1/admin/users?page=${page}&size=20`),
  getCourses: (page = 1) => request(`/api/v1/admin/courses?page=${page}&size=20`),
  deleteCourse: (id: string) => request(`/api/v1/admin/courses/${id}`, { method: "DELETE" }),
};

// Also add quizzes + projects + leaderboard to the generic api object
// (the named exports above are the primary interface)

export { ApiError };

// Generic client. All backend routes are mounted under /api/v1 (see backend/app/main.py).
// Normalize call sites that pass a bare path (e.g. "/learn/...") so they resolve correctly.
const API_PREFIX = "/api/v1";

function withPrefix(endpoint: string): string {
  if (endpoint.startsWith(API_PREFIX)) return endpoint;
  return `${API_PREFIX}${endpoint}`;
}

export const api = {
  get: <T = any>(endpoint: string) => request<T>(withPrefix(endpoint)),
  post: <T = any>(endpoint: string, body?: unknown) => request<T>(withPrefix(endpoint), { method: "POST", body }),
  put: <T = any>(endpoint: string, body?: unknown) => request<T>(withPrefix(endpoint), { method: "PUT", body }),
  patch: <T = any>(endpoint: string, body?: unknown) => request<T>(withPrefix(endpoint), { method: "PATCH", body }),
  delete: <T = any>(endpoint: string) => request<T>(withPrefix(endpoint), { method: "DELETE" }),
};
