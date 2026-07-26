"use client";

import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { generateRoadmap } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorMessage } from "@/components/ui/error-message";
import { useApiError } from "@/hooks/use-api-error";

export default function RoadmapGeneratorPage() {
  const [goal, setGoal] = useState("");
  const [experience, setExperience] = useState("beginner");
  const [technologies, setTechnologies] = useState("");
  const [result, setResult] = useState<{
    title: string;
    description: string;
    stages: string[];
  } | null>(null);

  const { error, details, setError, reset } = useApiError();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    reset();
    setResult(null);
    try {
      const data = await generateRoadmap({
        goal,
        experience,
        technologies: technologies
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      });
      setResult({ title: data.title, description: data.description, stages: data.stages });
    } catch (err) {
      setError(err);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-foreground">AI Roadmap Generator</h1>
        <p className="text-muted-foreground">
          Tell us your goal and we will build a personalized learning path.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="goal">Goal</Label>
          <Input
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., Become a full-stack developer"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="experience">Experience</Label>
          <select
            id="experience"
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
            className="mt-1 w-full rounded-xl border border-border bg-card px-4 py-2.5 text-sm text-foreground focus:border-primary focus:ring-primary"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div>
          <Label htmlFor="technologies">Technologies (comma-separated)</Label>
          <Input
            id="technologies"
            value={technologies}
            onChange={(e) => setTechnologies(e.target.value)}
            placeholder="e.g., Python, React, SQL"
            className="mt-1"
          />
        </div>
        {error && <ErrorMessage details={details}>{error}</ErrorMessage>}
        <Button type="submit" disabled={!goal.trim()}>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate Roadmap
        </Button>
      </form>

      {result && (
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-bold text-card-foreground">{result.title}</h2>
          <p className="mt-2 text-muted-foreground">{result.description}</p>
          <ol className="mt-4 list-decimal space-y-2 pl-5 text-card-foreground">
            {result.stages.map((stage, i) => (
              <li key={i}>{stage}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
