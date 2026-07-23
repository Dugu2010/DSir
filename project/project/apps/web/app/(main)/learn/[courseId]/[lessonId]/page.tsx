"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock,
  Expand,
  GraduationCap,
  MessageCircle,
  NotebookPen,
  Play,
} from "lucide-react";
import {
  createNote,
  fetchCourseDetail,
  fetchLesson,
  fetchNoteForLesson,
  logActivity,
  updateLessonProgress,
  updateNote,
} from "@/lib/api";
import { CodeBlock } from "@/components/code-block";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useAIChat } from "@/hooks/use-ai-chat";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

function CodeRenderer({
  inline,
  children,
  className,
}: {
  inline?: boolean;
  children?: React.ReactNode;
  className?: string;
}) {
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : className?.replace("language-", "") || "text";
  const codeString = String(children).replace(/\n$/, "");
  if (!className || inline) {
    return (
      <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-sm dark:bg-slate-800">
        {children}
      </code>
    );
  }
  return <CodeBlock language={language} code={codeString} />;
}

function LessonContent({ content }: { content: Record<string, unknown> }) {
  const body = typeof content.body === "string" ? content.body : JSON.stringify(content, null, 2);

  return (
    <div className="prose prose-slate max-w-none dark:prose-invert">
      <ReactMarkdown
        components={{
          code: CodeRenderer,
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  );
}

export default function LearnPage() {
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"content" | "mentor" | "notes">("content");
  const [desktopRightTab, setDesktopRightTab] = useState<"mentor" | "notes">("mentor");
  const [isFocusMode, setIsFocusMode] = useState(false);
  const { messages, isChatting, sendMessage } = useAIChat();
  const [chatInput, setChatInput] = useState("");

  const {
    data: courseDetail,
    isLoading: courseLoading,
    error: courseError,
    refetch: refetchCourse,
  } = useQuery({
    queryKey: ["course-detail", courseId],
    queryFn: () => fetchCourseDetail(courseId),
  });

  const {
    data: lessonDetail,
    isLoading: lessonLoading,
    error: lessonError,
    refetch: refetchLesson,
  } = useQuery({
    queryKey: ["lesson-detail", lessonId],
    queryFn: () => fetchLesson(lessonId),
  });

  const { data: note, isLoading: noteLoading } = useQuery({
    queryKey: ["note", lessonId],
    queryFn: () => fetchNoteForLesson(lessonId),
  });

  const [noteContent, setNoteContent] = useState(note?.content ?? "");

  useEffect(() => {
    setNoteContent(note?.content ?? "");
  }, [note]);

  const noteMutation = useMutation({
    mutationFn: async () => {
      if (note) {
        await updateNote(note.id, { content: noteContent });
      } else {
        await createNote({ lesson_id: lessonId, content: noteContent });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["note", lessonId] });
    },
  });

  const markCompleteMutation = useMutation({
    mutationFn: () => updateLessonProgress(lessonId, true),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course-detail", courseId] });
    },
  });

  const allLessons = useMemo(
    () => courseDetail?.modules.flatMap((m) => m.lessons) ?? [],
    [courseDetail]
  );

  const currentIndex = allLessons.findIndex((l) => l.id === lessonId);
  const previousLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

  const currentModule = courseDetail?.modules.find((m) =>
    m.lessons.some((l) => l.id === lessonId)
  );

  useEffect(() => {
    if (lessonId) {
      logActivity("viewed_lesson", "lesson", lessonId).catch(() => null);
    }
  }, [lessonId]);

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    sendMessage(chatInput);
    setChatInput("");
  };

  const handleMarkComplete = () => {
    markCompleteMutation.mutate();
  };

  if (courseLoading || lessonLoading) {
    return <LearnSkeleton />;
  }

  if (courseError || lessonError || !courseDetail || !lessonDetail) {
    return (
      <div className="space-y-4">
        <ErrorMessage>
          Failed to load lesson.{" "}
          <Button onClick={() => { refetchCourse(); refetchLesson(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  const lesson = lessonDetail;
  const contentBody =
    typeof lesson.content === "object" && lesson.content !== null
      ? (lesson.content as Record<string, unknown>)
      : { body: String(lesson.content || "") };

  return (
    <div className={`flex flex-col gap-4 lg:flex-row ${isFocusMode ? "fixed inset-0 z-50 bg-background p-4" : "h-[calc(100vh-7rem)]"}`}>
      {/* Sidebar */}
      <aside className="hidden w-full flex-col overflow-hidden rounded-2xl border border-border bg-card lg:flex lg:w-72">
        <div className="border-b border-border p-4">
          <Link
            href={`/courses/${courseId}`}
            className="text-sm font-medium text-muted-foreground hover:text-foreground"
          >
            ← Back to course
          </Link>
          <h2 className="mt-2 line-clamp-2 text-lg font-bold">{courseDetail.course.title}</h2>
          <div className="mt-3">
            <Progress value={courseDetail.progress.progress_percent} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {courseDetail.progress.progress_percent}% complete
          </p>
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          {courseDetail.modules.map((module) => (
            <div key={module.id} className="mb-4">
              <h3 className="px-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                {module.title}
              </h3>
              <ul className="mt-2 space-y-1">
                {module.lessons.map((l) => {
                  const isCurrent = l.id === lessonId;
                  const isCompleted = l.is_completed;
                  return (
                    <li key={l.id}>
                      <Link
                        href={`/learn/${courseId}/${l.id}`}
                        className={`flex items-start gap-2 rounded-lg px-2 py-2 text-sm transition ${
                          isCurrent
                            ? "bg-primary/10 text-primary"
                            : "text-muted-foreground hover:bg-accent"
                        }`}
                      >
                        {isCompleted ? (
                          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                        ) : (
                          <Circle className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                        )}
                        <span className={isCurrent ? "font-medium" : ""}>{l.title}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-border p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <GraduationCap className="h-4 w-4" />
                <span className="truncate">{currentModule?.title}</span>
                <span className="hidden sm:inline">•</span>
                <span className="hidden items-center gap-1 sm:flex">
                  <Clock className="h-3.5 w-3.5" />
                  {lesson.duration_minutes} min
                </span>
              </div>
              <h1 className="mt-1 text-xl font-bold text-foreground">{lesson.title}</h1>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsFocusMode((prev) => !prev)}
                className="hidden items-center gap-1 rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-muted-foreground transition hover:bg-accent lg:flex"
                title={isFocusMode ? "Exit focus mode" : "Focus mode"}
              >
                <Expand className="h-4 w-4" />
                {isFocusMode ? "Exit" : "Focus"}
              </button>
              <div className="flex items-center gap-2 lg:hidden">
                <Button
                  variant="secondary"
                  onClick={() => setActiveTab(activeTab === "content" ? "mentor" : "content")}
                >
                  {activeTab === "content" ? "AI Mentor" : "Content"}
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {activeTab === "content" ? (
            <div className="flex-1 overflow-y-auto p-4 lg:p-6">
              <LessonContent content={contentBody} />

              <div className="mt-8 flex flex-col gap-4 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex gap-2">
                  {previousLesson && (
                    <Link
                      href={`/learn/${courseId}/${previousLesson.id}`}
                      className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2 text-sm font-medium text-foreground transition hover:bg-accent"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Link>
                  )}
                  {nextLesson && (
                    <Link
                      href={`/learn/${courseId}/${nextLesson.id}`}
                      className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition hover:bg-primary/90"
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  )}
                </div>
                <Button
                  onClick={handleMarkComplete}
                  disabled={lesson.is_completed || markCompleteMutation.isPending}
                  className="gap-2"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  {lesson.is_completed
                    ? "Completed"
                    : markCompleteMutation.isPending
                    ? "Saving..."
                    : "Mark as Complete"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-4 lg:hidden">
              {activeTab === "mentor" ? (
                <AIMentorPanel
                  messages={messages}
                  isChatting={isChatting}
                  chatInput={chatInput}
                  setChatInput={setChatInput}
                  onSend={handleSendMessage}
                />
              ) : (
                <NotesPanel
                  content={noteContent}
                  setContent={setNoteContent}
                  onSave={() => noteMutation.mutate()}
                  isLoading={noteMutation.isPending}
                />
              )}
            </div>
          )}

          {/* Right panel desktop */}
          <div className="hidden w-96 flex-col border-l border-border bg-card lg:flex">
            <div className="flex border-b border-border">
              <button
                onClick={() => setDesktopRightTab("mentor")}
                className={`flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition ${
                  desktopRightTab === "mentor"
                    ? "border-b-2 border-primary text-primary"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <MessageCircle className="h-4 w-4" />
                AI Mentor
              </button>
              <button
                onClick={() => setDesktopRightTab("notes")}
                className={`flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition ${
                  desktopRightTab === "notes"
                    ? "border-b-2 border-primary text-primary"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <NotebookPen className="h-4 w-4" />
                Notes
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              {desktopRightTab === "mentor" ? (
                <AIMentorPanel
                  messages={messages}
                  isChatting={isChatting}
                  chatInput={chatInput}
                  setChatInput={setChatInput}
                  onSend={handleSendMessage}
                />
              ) : (
                <NotesPanel
                  content={noteContent}
                  setContent={setNoteContent}
                  onSave={() => noteMutation.mutate()}
                  isLoading={noteMutation.isPending}
                />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function NotesPanel({
  content,
  setContent,
  onSave,
  isLoading,
}: {
  content: string;
  setContent: (value: string) => void;
  onSave: () => void;
  isLoading: boolean;
}) {
  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-bold">My notes</h3>
        <Button onClick={onSave} disabled={isLoading} size="sm">
          {isLoading ? "Saving..." : "Save"}
        </Button>
      </div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write notes for this lesson..."
        className="flex-1 resize-none rounded-xl border border-border bg-background p-3 text-sm text-foreground outline-none focus:border-primary"
      />
    </div>
  );
}

function AIMentorPanel({
  messages,
  isChatting,
  chatInput,
  setChatInput,
  onSend,
}: {
  messages: Array<{ role: "user" | "assistant"; content: string }>;
  isChatting: boolean;
  chatInput: string;
  setChatInput: (value: string) => void;
  onSend: () => void;
}) {
  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-4 flex items-center gap-2">
        <MessageCircle className="h-5 w-5 text-primary" />
        <h3 className="font-bold">AI Mentor</h3>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Ask me anything about this lesson, your code, or related concepts.
          </p>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`rounded-lg p-2.5 text-sm ${
              message.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-accent text-accent-foreground"
            }`}
          >
            {message.content}
          </div>
        ))}
        {isChatting && <p className="text-sm text-muted-foreground">AI is typing...</p>}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSend()}
          placeholder="Ask a question..."
          className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
        />
        <Button onClick={onSend} disabled={isChatting} size="sm">
          Send
        </Button>
      </div>
    </div>
  );
}

function LearnSkeleton() {
  return (
    <div className="flex h-[calc(100vh-7rem)] gap-4">
      <div className="hidden w-72 flex-col gap-4 lg:flex">
        <Skeleton className="h-full" />
      </div>
      <div className="flex-1 space-y-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}
