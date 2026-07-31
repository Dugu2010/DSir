"use client";

import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/lib/auth";
import { Settings, User, Bell, Palette, Shield } from "lucide-react";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-ink flex items-center gap-2">
          <Settings className="h-7 w-7" />
          Settings
        </h1>
        <p className="text-ink-secondary mt-1">Manage your account and preferences.</p>
      </div>

      <div className="grid gap-6">
        {/* Appearance */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Palette className="h-5 w-5 text-brand-600" />
            <h2 className="font-semibold text-ink">Appearance</h2>
          </div>
          <div className="flex gap-3">
            {["light", "dark", "system"].map((theme) => (
              <button
                key={theme}
                className="px-4 py-2 rounded-xl border border-border text-sm font-medium text-ink-secondary hover:text-ink hover:border-ink-tertiary transition-all capitalize"
              >
                {theme}
              </button>
            ))}
          </div>
        </Card>

        {/* Notifications */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="h-5 w-5 text-brand-600" />
            <h2 className="font-semibold text-ink">Notifications</h2>
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
                  <div className="w-9 h-5 bg-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-brand-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                </label>
              </div>
            ))}
          </div>
        </Card>

        {/* Security */}
        <Card padding="md">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-5 w-5 text-brand-600" />
            <h2 className="font-semibold text-ink">Security</h2>
          </div>
          <div className="space-y-4">
            <Input label="Current Password" type="password" placeholder="Enter current password" />
            <Input label="New Password" type="password" placeholder="Enter new password" />
            <Input label="Confirm New Password" type="password" placeholder="Confirm new password" />
            <Button onClick={() => toast.success("Password updated!")}>Update Password</Button>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card padding="md" className="border-red-200 dark:border-red-900">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-red-600">Danger Zone</h2>
              <p className="text-sm text-ink-tertiary mt-1">Sign out from all devices.</p>
            </div>
            <Button
              variant="danger"
              onClick={() => {
                logout();
                toast.success("Signed out from all devices");
              }}
            >
              Sign Out Everywhere
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
