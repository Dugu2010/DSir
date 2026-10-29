"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect } from "react";
import { ai as aiApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageLoader } from "@/components/ui/States";
import {
  Sparkles, Send, Bot, User, Plus, MessageSquare,
  Code2, GraduationCap, Bug, Briefcase, Trash2,
} from "lucide-react";
import toast from "react-hot-toast";

const assistants = [
  { type: "tutor", label: "AI Tutor", icon: GraduationCap, desc: "Learn concepts step-by-step" },
  { type: "reviewer", label: "Code Reviewer", icon: Code2, desc: "Get your code reviewed" },
  { type: "debugger", label: "Debugger", icon: Bug, desc: "Find and fix bugs" },
  { type: "career", label: "Career Advisor", icon: Briefcase, desc: "Career guidance" },
  { type: "mentor", label: "Mentor", icon: Sparkles, desc: "Industry best practices" },
];

export default function AIPage() {
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [activeConv, setActiveConv] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const { data: conversations, isLoading: convLoading } = useQuery({
    queryKey: ["ai-conversations"],
    queryFn: () => aiApi.getConversations(),
  });

  const { data: messages } = useQuery({
    queryKey: ["ai-messages", activeConv],
    queryFn: () => aiApi.getMessages(activeConv!),
    enabled: !!activeConv,
  });

  const createConvMutation = useMutation({
    mutationFn: (type: string) => aiApi.createConversation({ assistant_type: type }),
    onSuccess: (data) => {
      setActiveConv(data.id);
      queryClient.invalidateQueries({ queryKey: ["ai-conversations"] });
    },
  });

  const sendMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!activeConv) return;
      return aiApi.sendMessage(activeConv, content);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-messages", activeConv] });
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Unable to send your message. Please try again.");
    },
    onSettled: () => setSending(false),
  });

  const handleSend = () => {
    if (!input.trim() || !activeConv) return;
    setSending(true);
    sendMutation.mutate(input);
    setInput("");
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const activeConversation = conversations?.find((c) => c.id === activeConv);

  return (
    <div className="w-full min-w-0 space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 07 · Intelligent runtime
          </p>
          <h1 className="font-display text-3xl font-medium tracking-tight text-ink mt-2">
            Kernel <span className="italic text-coral-600 dark:text-coral-400">Co-Pilot.</span>
          </h1>
          <p className="text-ink-secondary mt-1">Get help from AI tutors, reviewers, and mentors.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
          <span className="rounded-full border border-border dark:border-white/10 px-3 py-1.5 tabular-nums">
            {assistants.length} engines
          </span>
          <span className="rounded-full border border-border dark:border-white/10 px-3 py-1.5 tabular-nums">
            {conversations?.length ?? 0} threads
          </span>
        </div>
      </header>

      <div className="flex w-full min-w-0 flex-col md:flex-row gap-4 md:gap-6 h-[calc(100dvh-16rem)] min-h-[26rem] md:h-[calc(100dvh-14rem)]">
        {/* Sidebar - Conversations */}
        <div className="w-full md:w-72 md:flex-shrink-0 max-h-[45%] md:max-h-none min-h-0 border-b md:border-b-0 md:border-r border-border dark:border-white/10 pb-3 md:pb-0 md:pr-4 flex flex-col">
          {/* Assistant buttons */}
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary mb-2 px-1">{"// "}Engines</p>
          <div className="space-y-1 mb-4">
            {assistants.map((a) => (
              <button
                key={a.type}
                onClick={() => createConvMutation.mutate(a.type)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-left transition-colors text-ink-secondary hover:text-ink hover:bg-surface-secondary dark:hover:bg-white/5"
              >
                <a.icon className="h-4 w-4 flex-shrink-0 text-coral-600 dark:text-coral-400" />
                <div className="min-w-0">
                  <div className="font-medium truncate">{a.label}</div>
                  <div className="text-xs text-ink-tertiary truncate">{a.desc}</div>
                </div>
                <Plus className="h-4 w-4 ml-auto flex-shrink-0" />
              </button>
            ))}
          </div>

          <div className="h-px bg-border dark:bg-white/10 my-2" />

          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary mb-2 px-1 mt-2">{"// "}Threads</p>
          {/* Conversation list */}
          <div className="flex-1 overflow-y-auto space-y-1">
            {convLoading ? (
              <div className="text-center text-sm text-ink-tertiary py-4">Loading...</div>
            ) : conversations && conversations.length > 0 ? (
              conversations.map((conv) => {
                const assistantInfo = assistants.find((a) => a.type === conv.assistant_type);
                const isActive = activeConv === conv.id;
                return (
                  <div
                    key={conv.id}
                    className={`group flex items-center gap-2 rounded-lg border transition-colors ${
                      isActive
                        ? "border-coral-500/30 bg-coral-50 dark:bg-coral-500/10 text-coral-700 dark:text-coral-400"
                        : "border-transparent text-ink-secondary hover:bg-surface-secondary dark:hover:bg-white/5"
                    }`}
                  >
                    <button
                      onClick={() => setActiveConv(conv.id)}
                      aria-pressed={isActive}
                      className="flex-1 flex items-center gap-2 px-3 py-2.5 text-sm text-left min-w-0"
                    >
                      <MessageSquare className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
                      <span className="flex-1 truncate">{conv.title || assistantInfo?.label || "Chat"}</span>
                    </button>
                    <button
                      onClick={() => {
                        aiApi.deleteConversation(conv.id)
                          .then(() => {
                            queryClient.invalidateQueries({ queryKey: ["ai-conversations"] });
                            if (activeConv === conv.id) setActiveConv(null);
                            toast.success("Conversation deleted");
                          })
                          .catch(() => toast.error("Failed to delete conversation"));
                      }}
                      className="p-1.5 mr-1 rounded hover:bg-surface-tertiary flex-shrink-0 opacity-0 group-hover:opacity-100 focus-visible:opacity-100"
                      aria-label={`Delete conversation ${conv.title || "with " + (assistantInfo?.label || "AI")}`}
                    >
                      <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                    </button>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-sm text-ink-tertiary py-8 px-3">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-40" />
                Start a conversation with an AI assistant
              </div>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col min-w-0 min-h-0">
          {activeConv ? (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 pb-4">
                {messages?.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                  >
                    {msg.role === "assistant" && (
                      <div className="h-8 w-8 rounded-md border border-coral-500/30 bg-coral-500/10 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-coral-600 dark:text-coral-400" />
                      </div>
                    )}
                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "bg-coral-500 text-night-600 rounded-tr-sm"
                          : "bg-surface border border-border dark:border-white/10 text-ink rounded-tl-sm"
                      }`}
                    >
                      <div className="prose-lesson prose-sm" style={{ maxWidth: "none" }}>{msg.content}</div>
                    </div>
                    {msg.role === "user" && (
                      <div className="h-8 w-8 rounded-md border border-border dark:border-white/10 bg-surface-secondary flex items-center justify-center flex-shrink-0">
                        <User className="h-4 w-4 text-ink-tertiary" />
                      </div>
                    )}
                  </div>
                ))}
                {sending && (
                  <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-md border border-coral-500/30 bg-coral-500/10 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-coral-600 dark:text-coral-400 animate-pulse" />
                    </div>
                    <div className="bg-surface border border-border dark:border-white/10 rounded-lg rounded-tl-sm px-4 py-3 text-sm">
                      <div className="flex gap-1">
                        <div className="h-1.5 w-1.5 rounded-full bg-ink-tertiary animate-bounce" />
                        <div className="h-1.5 w-1.5 rounded-full bg-ink-tertiary animate-bounce" style={{ animationDelay: "0.1s" }} />
                        <div className="h-1.5 w-1.5 rounded-full bg-ink-tertiary animate-bounce" style={{ animationDelay: "0.2s" }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="pt-4 border-t border-border dark:border-white/10">
                <div className="flex gap-3">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                    placeholder={`Ask ${assistants.find((a) => a.type === activeConversation?.assistant_type)?.label || "the AI"}...`}
                    aria-label="Message the AI assistant"
                    className="flex-1 h-12 px-4 rounded-lg border border-border dark:border-white/10 bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 placeholder:text-ink-tertiary"
                  />
                  <Button
                    size="lg"
                    onClick={handleSend}
                    loading={sending}
                    disabled={!input.trim()}
                    className="h-12 w-12 p-0 flex items-center justify-center"
                  >
                    <Send className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="h-14 w-14 rounded-xl border border-coral-500/30 bg-coral-500/10 flex items-center justify-center mx-auto mb-5">
                  <Sparkles className="h-7 w-7 text-coral-600 dark:text-coral-400" />
                </div>
                <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-tertiary mb-2">
                  {"// "}Session idle
                </p>
                <h2 className="font-display text-2xl font-medium text-ink mb-2">Your AI Learning Partner</h2>
                <p className="text-ink-secondary mb-8">
                  Choose an assistant to get started. Get help with concepts, code reviews, debugging, and career advice.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {assistants.slice(0, 4).map((a) => (
                    <button
                      key={a.type}
                      onClick={() => createConvMutation.mutate(a.type)}
                      className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border dark:border-white/10 hover:border-coral-400/60 dark:hover:border-coral-500/40 hover:bg-coral-50/40 dark:hover:bg-coral-500/5 transition-colors text-center"
                    >
                      <a.icon className="h-6 w-6 text-coral-600 dark:text-coral-400" />
                      <span className="text-sm font-medium text-ink">{a.label}</span>
                      <span className="text-xs text-ink-tertiary">{a.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
