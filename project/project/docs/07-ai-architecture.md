# AI Architecture: DSir

## 1. Overview

DSir's AI layer is provider-agnostic. It abstracts AI capabilities behind internal services so that switching between Gemini, OpenAI, Anthropic, Ollama, or Mock providers requires no changes to business logic.

## 2. Design Principles

- **Provider agnostic:** Business logic never depends on a specific AI provider SDK.
- **Composable:** AI capabilities are broken into small, reusable services.
- **Observable:** All AI requests and responses are logged for debugging and improvement.
- **Fallback-ready:** Support for fallback providers and mock providers for testing.
- **Cost-aware:** Token usage and latency are tracked per request.

## 3. AI Capabilities

| Capability | Description |
|------------|-------------|
| Mentor Chat | Context-aware tutoring and explanations |
| Code Review | Analyze code for correctness, style, and improvements |
| Debugger | Help learners identify and fix bugs |
| Content Generation | Generate exercises, explanations, and project ideas |
| Recommendation | Suggest next lessons, concepts, or projects |
| Interview Prep | Conduct mock interviews and evaluate responses |
| Curriculum Planning | Build personalized learning paths |

## 4. Provider Abstraction

```
┌─────────────────────────────────────────┐
│           AI Service Layer              │
│  (MentorService, ReviewService, etc.)   │
├─────────────────────────────────────────┤
│         Provider Interface              │
│  generate_text(), embed(), review()     │
├─────────────────────────────────────────┤
│  Gemini │ OpenAI │ Anthropic │ Ollama   │
└─────────────────────────────────────────┘
```

## 5. Provider Interface

```python
class AIProvider(Protocol):
    async def generate_text(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> TextResponse: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...
```

## 6. Configuration

Providers are configured via environment variables:

```env
AI_DEFAULT_PROVIDER=openai
AI_FALLBACK_PROVIDERS=anthropic,gemini
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
OLLAMA_BASE_URL=...
```

## 7. Prompt Management

- Prompts are stored as versioned templates in the codebase and database.
- Each capability has a base prompt and dynamic context injection.
- Prompts include learner history, current concept, and constraints.
- A/B testing and prompt versioning are supported.

## 8. Context Injection

Every AI request includes:
- Learner profile and goals
- Current course/roadmap progress
- Recent mistakes and strengths
- Current concept and lesson context
- Relevant retrieved context via RAG (pgvector)
- Previous conversation history (truncated to fit token limits)

## 9. Streaming

AI mentor responses are streamed to the client using Server-Sent Events (SSE) to minimize perceived latency and improve user experience.

```python
from fastapi.responses import StreamingResponse

async def mentor_stream(messages: list[Message]) -> StreamingResponse:
    async def event_generator():
        async for chunk in provider.generate_stream(messages):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

## 10. Safety & Moderation

- Input and output are filtered for harmful content
- Code execution is sandboxed
- AI responses are tagged and logged
- Rate limits prevent abuse

## 10. Observability

- Log provider, model, tokens used, latency, and cost
- Store request/response pairs for analysis
- Track error rates and fallback events
