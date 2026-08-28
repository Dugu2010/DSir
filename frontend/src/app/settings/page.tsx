"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/lib/auth";
import { auth as authApi } from "@/lib/api";
import { useTheme } from "@/lib/theme";
import { Settings, User, Bell, Palette, Shield, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const { logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) {
      toast.error("Please fill in all password fields.");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match.");
      return;
    }
    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setChangingPassword(true);
    try {
      await authApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      toast.success("Password updated!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      toast.error(err?.detail || err?.message || "Failed to update password");
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <p className="eyebrow mb-2 !text-coral-400">Preferences</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight flex items-center gap-2">
          <Settings className="h-7 w-7" />
          Settings
        </h1>
        <p className="text-paper-50/70 dark:text-ink-secondary mt-1">Manage your account and preferences.</p>
      </div>

      <div className="grid gap-6">
        {/* Appearance */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Palette className="h-5 w-5 text-coral-600 dark:text-coral-400" />
            <h2 className="font-display text-lg font-semibold text-ink">Appearance</h2>
          </div>
          <div className="flex flex-wrap gap-3" role="group" aria-label="Color theme">
            {(["light", "dark", "system"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                aria-pressed={theme === t}
                className={cn(
                  "flex items-center gap-1.5 px-4 py-2 rounded-xl border text-sm font-medium transition-all capitalize",
                  theme === t
                    ? "border-coral-500 bg-coral-50 text-coral-700 dark:bg-coral-500/10 dark:text-coral-400"
                    : "border-border dark:border-white/10 text-ink-secondary hover:text-ink hover:border-coral-400/50 dark:hover:border-coral-500/40"
                )}
              >
                {theme === t && <Check className="h-3.5 w-3.5" aria-hidden="true" />}
                {t}
              </button>
            ))}
          </div>
        </Card>

        {/* Notifications */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="h-5 w-5 text-coral-600 dark:text-coral-400" />
            <h2 className="font-display text-lg font-semibold text-ink">Notifications</h2>
          </div>
          <div className="space-y-3">
            {[
              { label: "Email notifications", desc: "Receive course updates and reminders" },
              { label: "Push notifications", desc: "Get notified in your browser" },
              { label: "Weekly digest", desc: "Summary of your weekly progress" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm font-medium text-ink">{item.label}</p>
                  <p className="text-xs text-ink-tertiary">{item.desc}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-9 h-5 bg-border dark:bg-white/15 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-coral-500 peer-focus:ring-offset-2 dark:peer-focus:ring-offset-night-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-coral-500 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                </label>
              </div>
            ))}
          </div>
        </Card>

        {/* Security */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-5 w-5 text-coral-600 dark:text-coral-400" />
            <h2 className="font-display text-lg font-semibold text-ink">Security</h2>
          </div>
          <div className="space-y-4">
            <Input label="Current Password" type="password" placeholder="Enter current password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
            <Input label="New Password" type="password" placeholder="Enter new password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
            <Input label="Confirm New Password" type="password" placeholder="Confirm new password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            <Button onClick={handleChangePassword} loading={changingPassword}>Update Password</Button>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card padding="md" className="border-red-200 dark:border-red-500/20">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display font-semibold text-red-600 dark:text-red-400">Sign Out</h2>
              <p className="text-sm text-ink-tertiary mt-1">Sign out of DSir on this device.</p>
            </div>
            <Button
              variant="danger"
              onClick={() => {
                logout();
                toast.success("Signed out");
              }}
            >
              Sign Out
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
