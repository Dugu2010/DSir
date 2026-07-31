"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect } from "react";
import { ai as aiApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
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
      setSending(false);
    },
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
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-ink flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-brand-600" />
          AI Assistant
        </h1>
        <p className="text-ink-secondary mt-1">Get help from AI tutors, reviewers, and mentors.</p>
      </div>

      <div className="flex gap-6 h-[calc(100vh-16rem)]">
        {/* Sidebar - Conversations */}
        <div className="w-72 flex-shrink-0 border-r border-border pr-4 flex flex-col">
          {/* Assistant buttons */}
          <div className="space-y-1 mb-4">
            {assistants.map((a) => (
              <button
                key={a.type}
                onClick={() => createConvMutation.mutate(a.type)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-left transition-all text-ink-secondary hover:text-ink hover:bg-surface-secondary"
              >
                <a.icon className="h-4 w-4 flex-shrink-0" />
                <div>
                  <div className="font-medium">{a.label}</div>
                  <div className="text-xs text-ink-tertiary">{a.desc}</div>
                </div>
                <Plus className="h-4 w-4 ml-auto flex-shrink-0" />
              </button>
            ))}
          </div>

          <div className="h-px bg-border my-2" />

          {/* Conversation list */}
          <div className="flex-1 overflow-y-auto space-y-1">
            {convLoading ? (
              <div className="text-center text-sm text-ink-tertiary py-4">Loading...</div>
            ) : conversations && conversations.length > 0 ? (
              conversations.map((conv) => {
                const assistantInfo = assistants.find((a) => a.type === conv.assistant_type);
                return (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConv(conv.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm text-left transition-all ${
                      activeConv === conv.id
                        ? "bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-400"
                        : "text-ink-secondary hover:bg-surface-secondary"
                    }`}
                  >
                    <MessageSquare className="h-4 w-4 flex-shrink-0" />
                    <span className="flex-1 truncate">{conv.title || assistantInfo?.label || "Chat"}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        aiApi.deleteConversation(conv.id).then(() => {
                          queryClient.invalidateQueries({ queryKey: ["ai-conversations"] });
                          if (activeConv === conv.id) setActiveConv(null);
                          toast.success("Conversation deleted");
                        });
                      }}
                      className="p-1 rounded hover:bg-surface-tertiary flex-shrink-0 opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="h-3 w-3 text-ink-tertiary" />
                    </button>
                  </button>
                );
              })
            ) : (
              <div className="text-center text-sm text-ink-tertiary py-8">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-40" />
                Start a conversation with an AI assistant
              </div>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col min-w-0">
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
                      <div className="h-8 w-8 rounded-xl bg-brand-100 dark:bg-brand-900 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-brand-600 dark:text-brand-400" />
                      </div>
                    )}
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "bg-brand-600 text-white rounded-tr-md"
                          : "bg-surface border border-border text-ink rounded-tl-md"
                      }`}
                    >
                      <div className="prose-lesson prose-sm" style={{ maxWidth: "none" }}>{msg.content}</div>
                    </div>
                    {msg.role === "user" && (
                      <div className="h-8 w-8 rounded-xl bg-surface-secondary flex items-center justify-center flex-shrink-0">
                        <User className="h-4 w-4 text-ink-tertiary" />
                      </div>
                    )}
                  </div>
                ))}
                {sending && (
                  <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-xl bg-brand-100 dark:bg-brand-900 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-brand-600 animate-pulse" />
                    </div>
                    <div className="bg-surface border border-border rounded-2xl rounded-tl-md px-4 py-3 text-sm">
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
              <div className="pt-4 border-t border-border">
                <div className="flex gap-3">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                    placeholder={`Ask ${activeConversation?.assistant_type || "the AI"}...`}
                    className="flex-1 h-12 px-4 rounded-xl border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 placeholder:text-ink-tertiary"
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
                <Sparkles className="h-16 w-16 text-brand-600 mx-auto mb-6" />
                <h2 className="text-2xl font-bold text-ink mb-2">Your AI Learning Partner</h2>
                <p className="text-ink-secondary mb-8">
                  Choose an assistant to get started. Get help with concepts, code reviews, debugging, and career advice.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {assistants.slice(0, 4).map((a) => (
                    <button
                      key={a.type}
                      onClick={() => createConvMutation.mutate(a.type)}
                      className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-border hover:border-brand-300 hover:bg-brand-50/50 dark:hover:bg-brand-950/30 transition-all text-center"
                    >
                      <a.icon className="h-6 w-6 text-brand-600" />
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
