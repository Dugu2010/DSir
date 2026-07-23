"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { AlertCircle, Check, Loader2, Moon, Sun, Trash2 } from "lucide-react";
import { changePassword, deleteAccount, fetchMe, fetchProfile, logout, updateProfile } from "@/lib/api";
import { useAuthStore } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardTitle } from "@/components/ui/card";
import { ErrorMessage } from "@/components/ui/error-message";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";

export default function SettingsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { theme, setTheme } = useTheme();
  const { logout: logoutStore } = useAuthStore();
  const [activeTab, setActiveTab] = useState<"profile" | "account" | "appearance">("profile");

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
  });

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: fetchProfile,
  });

  const isLoading = userLoading || profileLoading;

  const [profileForm, setProfileForm] = useState({
    full_name: "",
    daily_goal_minutes: 30,
  });

  useEffect(() => {
    if (user || profile) {
      setProfileForm({
        full_name: user?.full_name ?? "",
        daily_goal_minutes: profile?.daily_goal_minutes ?? 30,
      });
    }
  }, [user, profile]);

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const updateProfileMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
      setMessage({ type: "success", text: "Profile updated successfully." });
    },
    onError: (err: Error) => {
      setMessage({ type: "error", text: err.message || "Failed to update profile." });
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
      setMessage({ type: "success", text: "Password changed successfully." });
    },
    onError: (err: Error) => {
      setMessage({ type: "error", text: err.message || "Failed to change password." });
    },
  });

  const deleteAccountMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: async () => {
      await logout();
      logoutStore();
      router.push("/");
    },
    onError: (err: Error) => {
      setMessage({ type: "error", text: err.message || "Failed to delete account." });
    },
  });

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate({
      full_name: profileForm.full_name,
      daily_goal_minutes: Number(profileForm.daily_goal_minutes),
    });
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setMessage({ type: "error", text: "New passwords do not match." });
      return;
    }
    changePasswordMutation.mutate({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
  };

  const navItemClass = (tab: string) =>
    `w-full text-left rounded-lg px-4 py-2.5 text-sm font-medium transition ${
      activeTab === tab
        ? "bg-primary/10 text-primary"
        : "text-muted-foreground hover:bg-accent hover:text-foreground"
    }`;

  return (
    <div className="mx-auto max-w-5xl animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account, preferences, and appearance.</p>
      </div>

      {message && (
        <div
          className={`mb-6 flex items-center gap-2 rounded-lg p-4 text-sm ${
            message.type === "success"
              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"
              : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300"
          }`}
        >
          {message.type === "error" ? <AlertCircle className="h-4 w-4" /> : <Check className="h-4 w-4" />}
          {message.text}
          <button onClick={() => setMessage(null)} className="ml-auto text-xs underline">
            Dismiss
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
        <aside className="md:col-span-1">
          <nav className="space-y-1">
            <button onClick={() => setActiveTab("profile")} className={navItemClass("profile")}>
              Profile
            </button>
            <button onClick={() => setActiveTab("appearance")} className={navItemClass("appearance")}>
              Appearance
            </button>
            <button onClick={() => setActiveTab("account")} className={navItemClass("account")}>
              Account
            </button>
          </nav>
        </aside>

        <div className="md:col-span-3">
          {activeTab === "profile" && (
            <Card>
              <CardTitle>Profile</CardTitle>
              <p className="mt-2 text-sm text-muted-foreground">Update your public profile and learning goals.</p>
              {isLoading ? (
                <Skeleton className="mt-6 h-48" />
              ) : (
                <form onSubmit={handleProfileSubmit} className="mt-6 space-y-4">
                  <div>
                    <Label htmlFor="full_name">Full name</Label>
                    <Input
                      id="full_name"
                      type="text"
                      value={profileForm.full_name}
                      onChange={(e) => setProfileForm((prev) => ({ ...prev, full_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="daily_goal">Daily goal (minutes)</Label>
                    <Input
                      id="daily_goal"
                      type="number"
                      min={5}
                      max={240}
                      value={profileForm.daily_goal_minutes}
                      onChange={(e) =>
                        setProfileForm((prev) => ({ ...prev, daily_goal_minutes: Number(e.target.value) }))
                      }
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button type="submit" disabled={updateProfileMutation.isPending}>
                      {updateProfileMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Save changes
                    </Button>
                  </div>
                </form>
              )}
            </Card>
          )}

          {activeTab === "appearance" && (
            <Card>
              <CardTitle>Appearance</CardTitle>
              <p className="mt-2 text-sm text-muted-foreground">Choose how DSir looks on your device.</p>
              <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
                {(["light", "dark", "system"] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`rounded-xl border p-4 text-left transition ${
                      theme === t
                        ? "border-primary bg-primary/5"
                        : "border-border bg-card hover:bg-accent"
                    }`}
                  >
                    <div className="mb-2 flex items-center gap-2 font-semibold capitalize">
                      {t === "dark" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                      {t}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {t === "system" ? "Follow your system preference." : `Use ${t} mode.`}
                    </p>
                  </button>
                ))}
              </div>
            </Card>
          )}

          {activeTab === "account" && (
            <div className="space-y-6">
              <Card>
                <CardTitle>Change password</CardTitle>
                <p className="mt-2 text-sm text-muted-foreground">Update your password to keep your account secure.</p>
                <form onSubmit={handlePasswordSubmit} className="mt-6 space-y-4">
                  <div>
                    <Label htmlFor="current_password">Current password</Label>
                    <Input
                      id="current_password"
                      type="password"
                      value={passwordForm.current_password}
                      onChange={(e) =>
                        setPasswordForm((prev) => ({ ...prev, current_password: e.target.value }))
                      }
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="new_password">New password</Label>
                    <Input
                      id="new_password"
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) =>
                        setPasswordForm((prev) => ({ ...prev, new_password: e.target.value }))
                      }
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="confirm_password">Confirm new password</Label>
                    <Input
                      id="confirm_password"
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) =>
                        setPasswordForm((prev) => ({ ...prev, confirm_password: e.target.value }))
                      }
                      required
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button type="submit" disabled={changePasswordMutation.isPending}>
                      {changePasswordMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Change password
                    </Button>
                  </div>
                </form>
              </Card>

              <Card className="border-red-200 dark:border-red-900/50">
                <CardTitle className="text-red-600 dark:text-red-400">Danger zone</CardTitle>
                <p className="mt-2 text-sm text-muted-foreground">
                  Deleting your account is permanent and cannot be undone.
                </p>
                <div className="mt-6">
                  <Button
                    variant="danger"
                    onClick={() => {
                      if (confirm("Are you sure you want to delete your account? This cannot be undone.")) {
                        deleteAccountMutation.mutate();
                      }
                    }}
                    disabled={deleteAccountMutation.isPending}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    {deleteAccountMutation.isPending ? "Deleting..." : "Delete account"}
                  </Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
