"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchConceptLessons, fetchLessonDetail, runCode, reviewCode } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { useAIChat } from "@/hooks/use-ai-chat";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function WorkspacePage() {
  const { conceptId } = useParams<{ conceptId: string }>();
  const [code, setCode] = useState("# Write your code here\nprint('Hello, DSir!')");
  const [output, setOutput] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const { messages, setMessages, isChatting, sendMessage } = useAIChat();
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

  const lessonContent: string = (() => {
    if (!lessonDetail?.content) return "No lesson content available.";
    if (typeof lessonDetail.content === "string") return lessonDetail.content;
    const body = (lessonDetail.content as Record<string, unknown>).body;
    if (typeof body === "string") return body;
    if (body !== undefined && body !== null) return String(body);
    return JSON.stringify(lessonDetail.content) ?? "No lesson content available.";
  })();
  const currentLesson = lessonList[currentLessonIndex];

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
        <div className="h-8 w-1/3 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
        <div className="h-[calc(100vh-8rem)] animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
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
        <div className="flex-1 overflow-auto rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          {/* Lesson navigation */}
          {lessonList.length > 1 && (
            <div className="mb-3 flex items-center gap-2 border-b border-slate-200 pb-3 dark:border-slate-700">
              {lessonList.map((l, i) => (
                <button
                  key={l.id}
                  onClick={() => setCurrentLessonIndex(i)}
                  className={`rounded px-2 py-1 text-xs font-medium transition ${
                    i === currentLessonIndex
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                      : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">
            {currentLesson?.title ?? "Lesson"}
          </h2>
          {currentLesson && (
            <span className="mt-1 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
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
        <div className="min-h-[300px] flex-1 overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">
          <Editor
            height="100%"
            language="python"
            value={code}
            onChange={(value) => setCode(value ?? "")}
            theme="vs-dark"
            options={{ minimap: { enabled: false }, fontSize: 14 }}
          />
        </div>
        <div className="h-40 rounded-2xl border border-slate-200 bg-slate-950 p-4 font-mono text-sm text-slate-100 dark:border-slate-700">
          <p className="text-slate-400">{output || "Console output..."}</p>
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
        <div className="flex flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <h3 className="font-bold text-slate-900 dark:text-white">AI Mentor</h3>
          <div className="mt-2 flex-1 space-y-3 overflow-auto">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`rounded-lg p-2 text-sm ${
                  message.role === "user"
                    ? "bg-blue-50 text-blue-900 dark:bg-blue-900/20 dark:text-blue-100"
                    : "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100"
                }`}
              >
                {message.content}
              </div>
            ))}
            {isChatting && <p className="text-sm text-slate-500">AI is typing...</p>}
          </div>
          <div className="mt-2 flex gap-2">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask a question..."
              className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
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
