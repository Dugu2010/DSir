"use client";

import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Trophy, Star, Flame, Award, Code2, BookOpen, Target, Zap } from "lucide-react";

const allAchievements = [
  { icon: "🐍", name: "Python Starter", desc: "Complete your first Python lesson", category: "learning", xp: 50, unlocked: true },
  { icon: "⚔️", name: "Code Warrior", desc: "Complete 10 coding exercises", category: "practice", xp: 100, unlocked: true },
  { icon: "🔥", name: "7-Day Streak", desc: "Maintain a 7-day learning streak", category: "streak", xp: 200, unlocked: true },
  { icon: "🎓", name: "Course Graduate", desc: "Complete your first course", category: "milestone", xp: 500, unlocked: false },
  { icon: "⭐", name: "Perfect Score", desc: "Get 100% on an exercise", category: "practice", xp: 75, unlocked: true },
  { icon: "🌅", name: "Early Bird", desc: "Complete 5 lessons before 9 AM", category: "special", xp: 150, unlocked: false },
  { icon: "💻", name: "Code Machine", desc: "Submit 50 exercise solutions", category: "practice", xp: 300, unlocked: false },
  { icon: "📚", name: "Bookworm", desc: "Complete 25 lessons", category: "learning", xp: 250, unlocked: false },
  { icon: "🏆", name: "Top 10", desc: "Reach the top 10 on weekly leaderboard", category: "social", xp: 400, unlocked: false },
  { icon: "🎯", name: "Goal Crusher", desc: "Complete daily goal 5 days in a row", category: "streak", xp: 150, unlocked: false },
];

export default function AchievementsPage() {
  const { user } = useAuth();
  const unlocked = allAchievements.filter((a) => a.unlocked).length;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-ink flex items-center gap-2">
          <Trophy className="h-8 w-8 text-amber-500" />
          Achievements
        </h1>
        <p className="text-ink-secondary mt-1">{unlocked}/{allAchievements.length} unlocked</p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {allAchievements.map((ach) => (
          <Card key={ach.name} padding="md" className={!ach.unlocked ? "opacity-50 grayscale" : ""}>
            <div className="flex items-start gap-4">
              <div className="text-3xl">{ach.icon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-ink">{ach.name}</h3>
                  {ach.unlocked && <Star className="h-4 w-4 text-amber-500 fill-amber-500" />}
                </div>
                <p className="text-sm text-ink-secondary mt-0.5">{ach.desc}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-surface-secondary text-ink-tertiary capitalize">
                    {ach.category}
                  </span>
                  <span className="text-xs text-ink-tertiary">{ach.xp} XP</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
