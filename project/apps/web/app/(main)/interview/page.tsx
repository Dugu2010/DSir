"use client";

import { useState } from "react";
import { Mic, Sparkles } from "lucide-react";
import { generateInterviewQuestion } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorMessage } from "@/components/ui/error-message";
import { useApiError } from "@/hooks/use-api-error";

export default function InterviewCoachPage() {
  const [role, setRole] = useState("");
  const [level, setLevel] = useState("mid-level");
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState<{
    question: string;
    hints: string[];
    follow_ups: string[];
  } | null>(null);

  const { error, details, setError, reset } = useApiError();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    reset();
    setResult(null);
    try {
      const data = await generateInterviewQuestion({ role, level, topic });
      setResult(data);
    } catch (err) {
      setError(err);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Interview Coach</h1>
        <p className="text-muted-foreground">
          Practice with AI-generated interview questions tailored to your target role.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="role">Target Role</Label>
          <Input
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g., Frontend Engineer"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="level">Level</Label>
          <select
            id="level"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="mt-1 w-full rounded-xl border border-border bg-card px-4 py-2.5 text-sm text-foreground focus:border-primary focus:ring-primary"
          >
            <option value="junior">Junior</option>
            <option value="mid-level">Mid-level</option>
            <option value="senior">Senior</option>
          </select>
        </div>
        <div>
          <Label htmlFor="topic">Topic (optional)</Label>
          <Input
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., React hooks"
            className="mt-1"
          />
        </div>
        {error && <ErrorMessage details={details}>{error}</ErrorMessage>}
        <Button type="submit" disabled={!role.trim()}>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate Question
        </Button>
      </form>

      {result && (
        <div className="space-y-6 rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div>
            <h2 className="flex items-center gap-2 text-xl font-bold text-card-foreground">
              <Mic className="h-5 w-5 text-primary" />
              Question
            </h2>
            <p className="mt-2 text-card-foreground">{result.question}</p>
          </div>
          <div>
            <h3 className="font-semibold text-card-foreground">Hints</h3>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
              {result.hints.map((hint, i) => (
                <li key={i}>{hint}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-card-foreground">Follow-ups</h3>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
              {result.follow_ups.map((followUp, i) => (
                <li key={i}>{followUp}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
