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

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2">Community</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
            <MessagesSquare className="h-8 w-8 text-coral-500" />
            Discussions
          </h1>
          <p className="text-ink-secondary mt-1">Ask questions and help fellow learners.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)} leftIcon={<Plus className="h-4 w-4" />} size="sm">
          New Thread
        </Button>
      </div>

      {/* New discussion form */}
      {showForm && (
        <Card padding="md">
          <h3 className="font-display font-semibold text-ink mb-4">Start a discussion</h3>
          <div className="space-y-3">
            <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. How do closures work in JS?" />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-ink">Content</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={4}
                placeholder="Describe your question in detail..."
                className="w-full px-3 py-2 rounded-xl border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500"
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
          {items.map((d) => (
            <Card key={d.id} padding="md" className={cn(openId === d.id && "border-coral-400/60 dark:border-coral-500/40")}>
              <button className="w-full text-left" onClick={() => setOpenId(openId === d.id ? null : d.id)}>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <h3 className="font-display font-semibold text-ink">{d.title}</h3>
                    <p className="text-xs text-ink-tertiary mt-0.5">by {d.display_name || "Anonymous"}</p>
                  </div>
                  {d.is_resolved && <Badge variant="success" size="sm">Resolved</Badge>}
                </div>
                <p className="text-sm text-ink-secondary line-clamp-2 mb-3">{d.content}</p>
                <div className="flex items-center gap-4 text-xs text-ink-tertiary">
                  <span>{formatDate(d.created_at)}</span>
                  <span className="flex items-center gap-1"><MessageCircle className="h-3.5 w-3.5" /> {d.reply_count} replies</span>
                  <span className="flex items-center gap-1"><ThumbsUp className="h-3.5 w-3.5" /> {d.vote_count}</span>
                </div>
              </button>

              {/* Expanded thread */}
              {openId === d.id && (
                <div className="mt-4 pt-4 border-t border-border dark:border-white/10 space-y-3">
                  {thread?.replies?.length ? (
                    thread.replies.map((r: DiscussionReply) => (
                      <div key={r.id} className={cn("flex gap-3", r.is_solution && "bg-emerald-50 dark:bg-emerald-500/5 border border-emerald-200 dark:border-emerald-500/20 rounded-xl p-3")}>
                        <div className="h-8 w-8 rounded-full bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center text-coral-500 font-semibold text-xs flex-shrink-0 mt-1">
                          {(r.user_id as string)?.slice(0, 1)?.toUpperCase() || "U"}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-ink">{r.display_name || "Anonymous"}</span>
                            {r.is_solution && <Badge variant="success" size="sm">Solution</Badge>}
                          </div>
                          <p className="text-sm text-ink mt-1 whitespace-pre-wrap">{r.content}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <button onClick={() => voteMutation.mutate({ replyId: r.id, direction: "up" })} className="flex items-center gap-1 text-xs text-ink-tertiary hover:text-ink">
                              <ThumbsUp className="h-3.5 w-3.5" /> {r.vote_count}
                            </button>
                            <button onClick={() => voteMutation.mutate({ replyId: r.id, direction: "down" })} className="flex items-center gap-1 text-xs text-ink-tertiary hover:text-ink">
                              <ThumbsDown className="h-3.5 w-3.5" />
                            </button>
                            {d.user_id === user?.id && !r.is_solution && (
                              <button onClick={() => markSolutionMutation.mutate(r.id)} className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
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
                      className="flex-1 h-10 px-3 rounded-xl border border-border bg-surface text-ink text-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500"
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
