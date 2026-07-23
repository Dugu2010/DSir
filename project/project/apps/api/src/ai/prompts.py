from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptTemplate:
    name: str
    template: str
    version: str = "1.0"

    def render(self, **kwargs: str) -> str:
        return self.template.format(**kwargs)


MENTOR_PROMPT = PromptTemplate(
    name="mentor",
    template="""You are a supportive programming mentor. A learner is asking about {concept}.

Context: {context}

Learner question: {question}

Provide a helpful, encouraging explanation that guides the learner.""",
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


class PromptManager:
    _templates: dict[str, PromptTemplate] = {
        "mentor": MENTOR_PROMPT,
        "code-review": CODE_REVIEW_PROMPT,
        "hint": HINT_PROMPT,
        "revision-problem": REVISION_PROBLEM_PROMPT,
    }

    @classmethod
    def get(cls, name: str) -> PromptTemplate:
        if name not in cls._templates:
            raise KeyError(f"Unknown prompt template: {name}")
        return cls._templates[name]

    @classmethod
    def list_templates(cls) -> list[str]:
        return list(cls._templates.keys())
