// ── Core Types for DSir Platform ──

export interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
  role: "student" | "teacher" | "admin" | "superadmin";
  email_verified: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface UserStats {
  total_xp: number;
  current_level: number;
  current_streak: number;
  longest_streak: number;
  lessons_completed: number;
  exercises_completed: number;
  projects_completed: number;
  total_time_spent_seconds: number;
}

export interface Course {
  id: string;
  title: string;
  slug: string;
  description: string;
  long_description: string | null;
  learning_objectives: string[] | null;
  prerequisites: string[] | null;
  difficulty: string;
  estimated_duration_minutes: number | null;
  status: string;
  image_url: string | null;
  thumbnail_url: string | null;
  language: string;
  skill_tags: string[] | null;
  module_count: number;
  lesson_count: number;
  enrollment_count: number;
  rating_average: number;
  rating_count: number;
  is_featured: boolean;
  is_free: boolean;
  author_id: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export interface CourseListItem {
  id: string;
  title: string;
  slug: string;
  description: string;
  difficulty: string;
  estimated_duration_minutes: number | null;
  image_url: string | null;
  thumbnail_url: string | null;
  skill_tags: string[] | null;
  module_count: number;
  lesson_count: number;
  enrollment_count: number;
  rating_average: number;
  is_featured: boolean;
  is_free: boolean;
  published_at: string | null;
}

export interface Module {
  id: string;
  course_id: string;
  title: string;
  slug: string;
  description: string | null;
  learning_objectives: string[] | null;
  display_order: number;
  lesson_count: number;
  estimated_duration_minutes: number | null;
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  description: string | null;
  content: string;
  content_markdown: string;
  learning_objectives: string[] | null;
  difficulty: string;
  estimated_duration_minutes: number | null;
  display_order: number;
  skill_tags: string[] | null;
  is_free_preview: boolean;
  version: number;
  status: string;
  published_at: string | null;
  created_at: string;
}

export interface Exercise {
  id: string;
  lesson_id: string | null;
  title: string;
  description: string;
  instructions: string;
  exercise_type: string;
  difficulty: string;
  starter_code: string | null;
  skill_tags: string[] | null;
  estimated_duration_minutes: number | null;
  points: number;
  hints_count: number;
}

export interface Submission {
  id: string;
  exercise_id: string;
  status: string;
  score: number | null;
  execution_time_ms: number | null;
  error_message: string | null;
  hints_used: number;
  attempt_number: number;
  submitted_at: string;
}

export interface Enrollment {
  id: string;
  course: Course;
  progress_percentage: number;
  is_completed: boolean;
  completed_at: string | null;
  enrolled_at: string;
  last_accessed_at: string;
}

export interface Dashboard {
  user: User;
  stats: UserStats;
  continue_learning: Enrollment[];
  recent_activity: ActivityItem[];
  daily_goal: DailyGoal | null;
  achievements: Achievement[];
  recommended_courses: CourseListItem[];
}

export interface ActivityItem {
  type: string;
  title: string;
  lesson_id?: string;
  at: string | null;
}

export interface DailyGoal {
  target_minutes: number;
  target_lessons: number;
  target_exercises: number;
  actual_minutes: number;
  actual_lessons: number;
  actual_exercises: number;
  is_completed: boolean;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  xp_reward: number;
  unlocked_at: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Flashcard {
  id: string;
  front_content: string;
  back_content: string;
  status: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_at: string | null;
}

export interface AIConversation {
  id: string;
  assistant_type: string;
  title: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface AIMessage {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
}
