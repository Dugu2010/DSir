from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptTemplate:
    name: str
    template: str
    version: str = "1.0"

    def render(self, **kwargs: str) -> str:
        return self.template.format(**kwargs)


MENTOR_SYSTEM_PROMPT = PromptTemplate(
    name="mentor-system",
    template="""You are DSir, a supportive programming mentor. The learner is currently working through: {context}.

Rules:
- Explain concepts clearly and concisely.
- Provide code examples when helpful.
- Do not give full solutions to exercises; guide the learner to discover the answer.
- Encourage best practices and debugging strategies.
- Keep responses focused on the current lesson context unless the learner asks something unrelated.""",
)

CODE_REVIEW_PROMPT = PromptTemplate(
    name="code-review",
    template="""Review the following {language} code for correctness, style, performance, and edge cases.

Context: {context}

```{language}
{code}
```

Provide feedback, specific suggestions, and identify any issues or bugs.""",
)

HINT_PROMPT = PromptTemplate(
    name="hint",
    template="""You are a programming mentor. A learner is working on a problem about "{concept}".

Problem: {problem}

Provide a helpful hint that guides them without giving the answer.""",
)

REVISION_PROBLEM_PROMPT = PromptTemplate(
    name="revision-problem",
    template=(
        "You are an adaptive revision engine. Create a fresh practice problem for the concept "
        '"{concept}".\n\n'
        "Difficulty target: {difficulty}\n"
        "Learner recent mistakes: {mistakes}\n\n"
        "Generate a concise problem statement and example input/output. "
        "Do not include the answer."
    ),
)


ROADMAP_GENERATOR_PROMPT = PromptTemplate(
    name="roadmap-generator",
    template="""Create a personalized learning roadmap.

Goal: {goal}
Experience level: {experience}
Relevant technologies: {technologies}

Return:
- A short title on the first line.
- A one-sentence description on the second line.
- 5-8 stages/milestones, each starting with "- ".""",
)

INTERVIEW_COACH_PROMPT = PromptTemplate(
    name="interview-coach",
    template="""You are an interview coach preparing someone for a {level} {role} interview.

Topic focus: {topic}

Generate one realistic interview question.
Provide 2-3 concise hints for the candidate.
Also provide 2 follow-up questions an interviewer might ask.

Format:
Question: <question>
Hint: <hint 1>
Hint: <hint 2>
Follow-up: <follow-up 1>
Follow-up: <follow-up 2>""",
)


class PromptManager:
    _templates: dict[str, PromptTemplate] = {
        "mentor": MENTOR_SYSTEM_PROMPT,
        "mentor-system": MENTOR_SYSTEM_PROMPT,
        "code-review": CODE_REVIEW_PROMPT,
        "hint": HINT_PROMPT,
        "revision-problem": REVISION_PROBLEM_PROMPT,
        "roadmap-generator": ROADMAP_GENERATOR_PROMPT,
        "interview-coach": INTERVIEW_COACH_PROMPT,
    }

    @classmethod
    def get(cls, name: str) -> PromptTemplate:
        if name not in cls._templates:
            raise KeyError(f"Unknown prompt template: {name}")
        return cls._templates[name]

    @classmethod
    def list_templates(cls) -> list[str]:
        return list(cls._templates.keys())
