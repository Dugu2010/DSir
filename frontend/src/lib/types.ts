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
  rating_count: number;
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

export interface LessonListItem {
  id: string;
  module_id: string;
  title: string;
  slug: string;
  description: string | null;
  difficulty: string;
  estimated_duration_minutes: number | null;
  display_order: number;
  is_free_preview: boolean;
  status: string;
}

export interface CourseStructure {
  id: string;
  course_id: string;
  title: string;
  slug: string;
  description: string | null;
  learning_objectives: string[] | null;
  display_order: number;
  lesson_count: number;
  estimated_duration_minutes: number | null;
  lessons: LessonListItem[];
}

export interface UserNote {
  id: string;
  lesson_id: string;
  content: string;
  is_private: boolean;
  created_at: string;
  updated_at: string;
}

export interface Certificate {
  id: string;
  course_id: string;
  certificate_number: string;
  issued_at: string;
  course_title: string;
  course_slug: string;
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

// ── Quizzes ────────────────────────────────────────────────────

export interface QuizListItem {
  id: string;
  title: string;
  description: string | null;
  passing_score: number;
  time_limit_minutes: number | null;
  question_count: number;
  course_title?: string | null;
  course_slug?: string | null;
}

export interface QuizDetail {
  id: string;
  title: string;
  description: string | null;
  passing_score: number;
  time_limit_minutes: number | null;
  questions: Question[];
}

export interface Question {
  id: string;
  question_type: string;
  content: string;
  explanation: string | null;
  points: number;
  options: QuestionOption[];
}

export interface QuestionOption {
  id: string;
  content: string;
  is_correct: boolean;
}

export interface QuizResult {
  quiz_id: string;
  score: number;
  passed: boolean;
  total_points: number;
  earned_points: number;
  correct_answers: number;
  total_questions: number;
  completed_at: string;
}

// ── Projects ───────────────────────────────────────────────────

export interface ProjectDetail {
  id: string;
  course_id: string | null;
  module_id: string | null;
  title: string;
  description: string;
  requirements: string;
  difficulty: string;
  is_capstone: boolean;
  estimated_duration_hours: number | null;
  skill_tags: string[] | null;
  starter_files: Record<string, unknown> | null;
}

export interface ProjectSubmission {
  id: string;
  project_id: string;
  code_files: Record<string, unknown>;
  review_status: string;
  review_feedback: string | null;
  review_score: number | null;
  submitted_at: string;
}

// ── Discussions ────────────────────────────────────────────────

export interface Discussion {
  id: string;
  lesson_id: string | null;
  user_id: string;
  display_name: string;
  title: string;
  content: string;
  is_resolved: boolean;
  vote_count: number;
  reply_count: number;
  created_at: string;
  updated_at: string;
  replies: DiscussionReply[];
}

export interface DiscussionReply {
  id: string;
  discussion_id: string;
  user_id: string;
  display_name: string;
  parent_id: string | null;
  content: string;
  is_solution: boolean;
  vote_count: number;
  created_at: string;
  updated_at: string;
}

// ── Leaderboard ────────────────────────────────────────────────

export interface LeaderboardEntry {
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  xp_earned: number;
  rank: number;
  current_level: number;
}

export interface UserRank {
  rank: number;
  xp_earned: number;
  period_type: string;
}

// ── Reviews & Knowledge ────────────────────────────────────────

export interface Review {
  id: string;
  user_id: string;
  display_name: string;
  rating: number;
  review: string | null;
  created_at: string;
}

export interface KnowledgeItem {
  topic: string;
  slug: string;
  mastery_level: number;
  confidence: number;
  assessment_count: number;
}
