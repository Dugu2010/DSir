"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchConceptLessons, fetchLessonDetail, runCode, reviewCode } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Skeleton } from "@/components/ui/skeleton";
import { useAIChat } from "@/hooks/use-ai-chat";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function WorkspacePage() {
  const { conceptId } = useParams<{ conceptId: string }>();
  const [code, setCode] = useState("# Write your code here\nprint('Hello, DSir!')");
  const [output, setOutput] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [chatInput, setChatInput] = useState("");

  const {
    data: lessons,
    isLoading: lessonsLoading,
    error: lessonsError,
    refetch: refetchLessons,
  } = useQuery({
    queryKey: ["concept-lessons", conceptId],
    queryFn: () => fetchConceptLessons(conceptId),
  });

  const lessonList = lessons?.items ?? [];
  const currentLessonId = lessonList[currentLessonIndex]?.id;

  const { data: lessonDetail } = useQuery({
    queryKey: ["lesson-detail", currentLessonId],
    queryFn: () => fetchLessonDetail(currentLessonId!),
    enabled: !!currentLessonId,
  });

  const currentLesson = lessonList[currentLessonIndex];
  const aiContext = currentLesson
    ? `Concept: ${currentLesson.title}. Lesson: ${currentLesson.title}. Language: ${currentLesson.lesson_type}.`
    : undefined;
  const { messages, setMessages, isChatting, sendMessage } = useAIChat(aiContext);

  const lessonContent: string = (() => {
    if (!lessonDetail?.content) return "No lesson content available.";
    if (typeof lessonDetail.content === "string") return lessonDetail.content;
    const body = (lessonDetail.content as Record<string, unknown>).body;
    if (typeof body === "string") return body;
    if (body !== undefined && body !== null) return String(body);
    return JSON.stringify(lessonDetail.content) ?? "No lesson content available.";
  })();

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const result = await runCode({ language: "python", code });
      setOutput(`${result.stdout}\n${result.stderr}`.trim());
    } catch {
      setOutput("Error running code.");
    } finally {
      setIsRunning(false);
    }
  };

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    sendMessage(chatInput);
    setChatInput("");
  };

  const handleReviewCode = async () => {
    try {
      const response = await reviewCode({ language: "python", code });
      setMessages((prev) => [...prev, { role: "assistant", content: `Code Review: ${response.feedback}` }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Code review failed." }]);
    }
  };

  if (lessonsLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-[calc(100vh-8rem)] rounded-2xl" />
      </div>
    );
  }

  if (lessonsError) {
    return (
      <div className="py-12">
        <ErrorMessage>
          Failed to load lesson.{" "}
          <Button onClick={() => refetchLessons()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-4 lg:flex-row">
      {/* Lesson Panel */}
      <div className="flex w-full flex-col gap-4 lg:w-1/4">
        <div className="flex-1 overflow-auto rounded-2xl border border-border bg-card p-4">
          {/* Lesson navigation */}
          {lessonList.length > 1 && (
            <div className="mb-3 flex items-center gap-2 border-b border-border pb-3">
              {lessonList.map((l, i) => (
                <button
                  key={l.id}
                  onClick={() => setCurrentLessonIndex(i)}
                  className={`rounded px-2 py-1 text-xs font-medium transition ${
                    i === currentLessonIndex
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
          <h2 className="text-lg font-bold text-card-foreground">
            {currentLesson?.title ?? "Lesson"}
          </h2>
          {currentLesson && (
            <span className="mt-1 inline-block rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
              {currentLesson.lesson_type}
            </span>
          )}
          <div className="prose prose-sm mt-4 max-w-none dark:prose-invert">
            {lessonContent}
          </div>
        </div>
      </div>

      {/* Editor & Console */}
      <div className="flex w-full flex-col gap-4 lg:w-1/2">
        <div className="min-h-[300px] flex-1 overflow-hidden rounded-2xl border border-border bg-card">
          <Editor
            height="100%"
            language="python"
            value={code}
            onChange={(value) => setCode(value ?? "")}
            theme="vs-dark"
            options={{ minimap: { enabled: false }, fontSize: 14 }}
          />
        </div>
        <div className="h-40 rounded-2xl border border-border bg-black p-4 font-mono text-sm text-foreground">
          <p className="text-muted-foreground">{output || "Console output..."}</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRun} disabled={isRunning} className="flex-1">
            {isRunning ? "Running..." : "Run Code"}
          </Button>
          <Button onClick={handleReviewCode} variant="secondary" className="flex-1">
            Review Code
          </Button>
        </div>
      </div>

      {/* AI Mentor */}
      <div className="flex w-full flex-col gap-4 lg:w-1/4">
        <div className="flex flex-1 flex-col rounded-2xl border border-border bg-card p-4">
          <h3 className="font-bold text-card-foreground">AI Mentor</h3>
          <div className="mt-2 flex-1 space-y-3 overflow-auto">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`rounded-lg p-2 text-sm ${
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
          <div className="mt-2 flex gap-2">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask a question..."
              className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
            />
            <Button onClick={handleSendMessage} disabled={isChatting} size="sm">
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
