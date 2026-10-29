"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { users } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { PageLoader } from "@/components/ui/States";
import { Bell, CheckCheck, Trophy, BookOpen, Flame, Info } from "lucide-react";
import toast from "react-hot-toast";

const iconMap: Record<string, React.ElementType> = {
  achievement: Trophy,
  course: BookOpen,
  streak: Flame,
  system: Info,
  reminder: Bell,
};

export default function NotificationsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => users.getNotifications(1),
  });

  const readAllMutation = useMutation({
    mutationFn: () => users.markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      toast.success("All marked as read");
    },
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => users.markNotificationRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  if (isLoading) return <PageLoader />;

  const notifications = data?.items || [];
  const unreadCount = notifications.filter((n: { is_read: boolean }) => !n.is_read).length;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-coral-600 dark:text-coral-400">
            {"// "}No. 13 · Activity feed
          </p>
          <h1 className="font-display text-3xl font-medium tracking-tight text-ink mt-2">
            Notifications
            {unreadCount > 0 && (
              <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-coral-600 dark:text-coral-400 border border-coral-500/30 bg-coral-500/5 rounded-full px-2.5 py-1 ml-3 align-middle">
                {unreadCount} new
              </span>
            )}
          </h1>
          <p className="text-ink-secondary mt-1">Stay updated on your progress and activity.</p>
        </div>
        {notifications.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => readAllMutation.mutate()}>
            <CheckCheck className="h-4 w-4 mr-1" /> Mark all read
          </Button>
        )}
      </div>

      {notifications.length > 0 ? (
        <div className="space-y-2">
          {notifications.map((n: { id: string; type: string; title: string; body: string | null; is_read: boolean; created_at: string }) => {
            const Icon = iconMap[n.type] || Info;
            return (
              <Card
                key={n.id}
                padding="md"
                onClick={!n.is_read ? () => markReadMutation.mutate(n.id) : undefined}
                className={`transition-colors ${!n.is_read ? "border-coral-500/25 bg-coral-500/[0.04] cursor-pointer" : ""}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0 border ${
                    !n.is_read
                      ? "border-coral-500/30 bg-coral-500/10"
                      : "border-border dark:border-white/10 bg-surface-secondary dark:bg-white/5"
                  }`}>
                    <Icon className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm ${!n.is_read ? "font-semibold text-ink" : "text-ink"}`}>{n.title}</p>
                      {!n.is_read && <div className="h-1.5 w-1.5 rounded-full bg-coral-500 flex-shrink-0" />}
                    </div>
                    {n.body && <p className="text-sm text-ink-secondary mt-0.5">{n.body}</p>}
                    <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-ink-tertiary mt-1.5">
                      {new Date(n.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <Bell className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
          <h3 className="font-display text-lg font-medium text-ink">No notifications yet</h3>
          <p className="text-sm text-ink-secondary mt-1">You&apos;ll receive notifications about your learning progress and achievements.</p>
        </div>
      )}
    </div>
  );
}
