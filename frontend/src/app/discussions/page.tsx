"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { discussions } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PageLoader, EmptyState, ErrorState } from "@/components/ui/States";
import { MessagesSquare, Plus, ThumbsUp, ThumbsDown, CheckCircle2, MessageCircle } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";
import toast from "react-hot-toast";
import type { Discussion, DiscussionReply } from "@/lib/types";

export default function DiscussionsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [openId, setOpenId] = useState<string | null>(null);
  const [replyText, setReplyText] = useState("");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["discussions"],
    queryFn: () => discussions.list(),
  });

  const { data: openThread } = useQuery({
    queryKey: ["discussion", openId],
    queryFn: () => discussions.get(openId!),
    enabled: !!openId,
  });

  const createMutation = useMutation({
    mutationFn: (d: { title: string; content: string }) => discussions.create(d),
    onSuccess: () => {
      setTitle(""); setContent(""); setShowForm(false);
      queryClient.invalidateQueries({ queryKey: ["discussions"] });
      toast.success("Discussion posted!");
    },
    onError: () => toast.error("Could not post discussion."),
  });

  const replyMutation = useMutation({
    mutationFn: (d: { discussionId: string; content: string }) =>
      discussions.addReply(d.discussionId, { content: d.content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["discussion", openId] });
      queryClient.invalidateQueries({ queryKey: ["discussions"] });
    },
    onError: () => toast.error("Could not post reply."),
  });

  const voteMutation = useMutation({
    mutationFn: (d: { replyId: string; direction: "up" | "down" }) =>
      discussions.voteReply(d.replyId, d.direction),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["discussion", openId] }),
    onError: (e: any) => toast.error(e?.detail || "Could not vote."),
  });

  const markSolutionMutation = useMutation({
    mutationFn: (replyId: string) => discussions.markSolution(replyId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["discussion", openId] }),
    onError: () => toast.error("Could not mark solution."),
  });

  if (isLoading) return <PageLoader label="Loading discussions..." />;
  if (error || !data) {
    return (
      <ErrorState title="Couldn't load discussions" description="Check your connection and try again." onRetry={() => refetch()} />
    );
  }

  const items: Discussion[] = data.items || [];
  const thread = openThread;
  const resolvedCount = items.filter((d) => d.is_resolved).length;
  const replyTotal = items.reduce((sum, d) => sum + d.reply_count, 0);
  const contributors = new Set(items.map((d) => d.user_id || d.display_name || d.id)).size;

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <header className="relative overflow-hidden rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <div className="p-6 md:p-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-5">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
              {"// "}No. 09 · Community &amp; peer review
            </p>
            <h1 className="font-display text-3xl md:text-4xl font-medium tracking-tight leading-[1.1] text-ink mt-3">
              Engineering{" "}
              <span className="italic text-coral-600 dark:text-coral-400">Discussions.</span>
            </h1>
            <p className="text-ink-secondary mt-2">
              Ask questions and help fellow learners.
            </p>
          </div>
          <Button onClick={() => setShowForm(!showForm)} leftIcon={<Plus className="h-4 w-4" />} size="sm" className="shrink-0">
            New Thread
          </Button>
        </div>
        {items.length > 0 && (
          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-border dark:bg-white/10 border-t border-border dark:border-white/10">
            {[
              { label: "Threads", value: items.length },
              { label: "Resolved", value: resolvedCount },
              { label: "Replies", value: replyTotal },
              { label: "Contributors", value: contributors },
            ].map((stat) => (
              <div key={stat.label} className="bg-surface dark:bg-night-500 px-4 py-3">
                <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">{stat.label}</dt>
                <dd className="font-display text-xl font-medium text-ink mt-0.5 tabular-nums">{stat.value}</dd>
              </div>
            ))}
          </dl>
        )}
      </header>

      {/* New discussion form */}
      {showForm && (
        <Card padding="md">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-1">
            {"// "}New thread
          </p>
          <h3 className="font-display font-medium text-ink mb-4">Start a discussion</h3>
          <div className="space-y-3">
            <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. How do closures work in JS?" />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-ink">Content</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={4}
                placeholder="Describe your question in detail..."
                className="w-full px-3 py-2 rounded-lg border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>Cancel</Button>
              <Button
                size="sm"
                disabled={!title.trim() || !content.trim()}
                loading={createMutation.isPending}
                onClick={() => createMutation.mutate({ title, content })}
              >
                Post
              </Button>
            </div>
          </div>
        </Card>
      )}

      {items.length === 0 ? (
        <EmptyState title="No discussions yet" description="Start the first conversation!" icon={<MessagesSquare className="h-8 w-8" />} />
      ) : (
        <div className="space-y-3">
          {items.map((d, index) => (
            <Card key={d.id} padding="md" className={cn(openId === d.id && "border-coral-400/60 dark:border-coral-500/40")}>
              <button className="w-full text-left" onClick={() => setOpenId(openId === d.id ? null : d.id)}>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-2">
                  <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400">
                    Thread // {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
                    {formatDate(d.created_at)}
                  </span>
                  {d.is_resolved && <Badge variant="success" size="sm" className="ml-auto">Resolved</Badge>}
                </div>
                <h3 className="font-display text-lg font-medium text-ink leading-snug">{d.title}</h3>
                <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary mt-1">
                  by {d.display_name || "Anonymous"}
                </p>
                <p className="text-sm text-ink-secondary line-clamp-2 mt-2 mb-3">{d.content}</p>
                <div className="flex items-center gap-4 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
                  <span className="flex items-center gap-1 tabular-nums">
                    <MessageCircle className="h-3.5 w-3.5" /> {d.reply_count} replies
                  </span>
                  <span className="flex items-center gap-1 tabular-nums">
                    <ThumbsUp className="h-3.5 w-3.5" /> {d.vote_count} votes
                  </span>
                </div>
              </button>

              {/* Expanded thread */}
              {openId === d.id && (
                <div className="mt-4 pt-4 border-t border-border dark:border-white/10 space-y-3">
                  <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">
                    {"// "}Replies
                  </p>
                  {thread?.replies?.length ? (
                    thread.replies.map((r: DiscussionReply) => (
                      <div key={r.id} className={cn("flex gap-3", r.is_solution && "bg-emerald-500/5 border border-emerald-500/25 rounded-lg p-3")}>
                        <div className="h-8 w-8 rounded-md bg-coral-500/10 border border-coral-500/30 flex items-center justify-center text-coral-600 dark:text-coral-400 font-mono text-xs flex-shrink-0 mt-1">
                          {(r.user_id as string)?.slice(0, 1)?.toUpperCase() || "U"}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-ink">{r.display_name || "Anonymous"}</span>
                            {r.is_solution && <Badge variant="success" size="sm">Solution</Badge>}
                          </div>
                          <p className="text-sm text-ink mt-1 whitespace-pre-wrap break-words">{r.content}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <button onClick={() => voteMutation.mutate({ replyId: r.id, direction: "up" })} className="flex items-center gap-1 font-mono text-[10px] text-ink-tertiary hover:text-coral-600 dark:hover:text-coral-400">
                              <ThumbsUp className="h-3.5 w-3.5" /> {r.vote_count}
                            </button>
                            <button onClick={() => voteMutation.mutate({ replyId: r.id, direction: "down" })} className="flex items-center gap-1 text-ink-tertiary hover:text-ink" aria-label="Downvote reply">
                              <ThumbsDown className="h-3.5 w-3.5" />
                            </button>
                            {d.user_id === user?.id && !r.is_solution && (
                              <button onClick={() => markSolutionMutation.mutate(r.id)} className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.1em] text-emerald-600 dark:text-emerald-400">
                                <CheckCircle2 className="h-3.5 w-3.5" /> Mark solution
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-ink-tertiary">No replies yet. Be the first to respond.</p>
                  )}

                  <div className="flex gap-2">
                    <input
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Write a reply..."
                      className="flex-1 h-10 px-3 rounded-lg border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && replyText.trim()) {
                          replyMutation.mutate({ discussionId: d.id, content: replyText });
                          setReplyText("");
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      disabled={!replyText.trim()}
                      loading={replyMutation.isPending}
                      onClick={() => { replyMutation.mutate({ discussionId: d.id, content: replyText }); setReplyText(""); }}
                    >
                      Reply
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
