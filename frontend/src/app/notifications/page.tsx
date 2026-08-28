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

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2">Updates</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink flex items-center gap-2">
            <Bell className="h-7 w-7" />
            Notifications
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
                className={`transition-all ${!n.is_read ? "bg-coral-50/40 dark:bg-coral-500/5 border-coral-200 dark:border-coral-500/20 cursor-pointer" : ""}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    !n.is_read ? "bg-coral-100 dark:bg-coral-500/10" : "bg-surface-secondary dark:bg-white/5"
                  }`}>
                    <Icon className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm ${!n.is_read ? "font-semibold text-ink" : "text-ink"}`}>{n.title}</p>
                      {!n.is_read && <div className="h-2 w-2 rounded-full bg-coral-500 flex-shrink-0" />}
                    </div>
                    {n.body && <p className="text-sm text-ink-secondary mt-0.5">{n.body}</p>}
                    <p className="text-xs text-ink-tertiary mt-1">
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
          <h3 className="font-display text-lg font-semibold text-ink">No notifications yet</h3>
          <p className="text-sm text-ink-secondary mt-1">You&apos;ll receive notifications about your learning progress and achievements.</p>
        </div>
      )}
    </div>
  );
}
