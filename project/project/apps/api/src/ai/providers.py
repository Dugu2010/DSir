from __future__ import annotations

import json
import os
import random
from collections.abc import AsyncGenerator

from src.ai.protocols import AIProvider, AIResponse, Message


class MockProvider(AIProvider):
    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        return AIResponse(
            content="This is a mock AI response for testing.",
            prompt_tokens=10,
            completion_tokens=10,
            model="mock",
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        chunks = ["This", "is", "a", "mock", "streaming", "response."]
        for chunk in chunks:
            yield chunk + " "

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        import hashlib

        seed = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(dimensions)]


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        try:
            import openai
        except ImportError as exc:
            raise ImportError("OpenAI SDK not installed. Install with `pip install openai`") from exc

        self.client = openai.AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
            dimensions=dimensions,
        )
        return list(response.data[0].embedding)

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        payload = [{"role": m.role.value, "content": m.content} for m in messages]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        return AIResponse(
            content=choice.message.content or "",
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            model=self.model,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        payload = [{"role": m.role.value, "content": m.content} for m in messages]
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20240620"):
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("Anthropic SDK not installed. Install with `pip install anthropic`") from exc

        self.client = anthropic.AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        payload = [{"role": m.role.value, "content": m.content} for m in messages if m.role.value != "system"]
        system_message = next((m.content for m in messages if m.role.value == "system"), None)
        response = await self.client.messages.create(
            model=self.model,
            messages=payload,
            system=system_message,
            temperature=temperature,
            max_tokens=max_tokens or 1024,
        )
        content = "".join(block.text for block in response.content)
        return AIResponse(
            content=content,
            prompt_tokens=response.usage.input_tokens if response.usage else 0,
            completion_tokens=response.usage.output_tokens if response.usage else 0,
            model=self.model,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        payload = [{"role": m.role.value, "content": m.content} for m in messages if m.role.value != "system"]
        system_message = next((m.content for m in messages if m.role.value == "system"), None)
        async with self.client.messages.stream(
            model=self.model,
            messages=payload,
            system=system_message,
            temperature=temperature,
            max_tokens=max_tokens or 1024,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        raise NotImplementedError("Anthropic does not provide a public embedding API")


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "Google Generative AI SDK not installed. Install with `pip install google-generativeai`"
            ) from exc

        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model
        self.client = genai.GenerativeModel(model_name=model)

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        prompt = "\n".join(f"{m.role.value}: {m.content}" for m in messages)
        response = await self.client.generate_content_async(prompt)
        return AIResponse(
            content=response.text or "",
            model=self.model,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        prompt = "\n".join(f"{m.role.value}: {m.content}" for m in messages)
        response = await self.client.generate_content_async(prompt, stream=True)
        async for chunk in response:
            text = chunk.text or ""
            if text:
                yield text

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        raise NotImplementedError("Gemini does not provide a public embedding API")


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str | None = None, model: str = "llama3"):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        import httpx

        payload = {
            "model": self.model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "stream": False,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        return AIResponse(
            content=data["message"]["content"],
            model=self.model,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        import httpx

        payload = {
            "model": self.model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "stream": True,
        }
        async with (
            httpx.AsyncClient() as client,
            client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response,
        ):
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = data.get("message", {})
                    content = message.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        import httpx

        payload = {"model": self.model, "prompt": text}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/embeddings", json=payload)
            response.raise_for_status()
            data = response.json()
        return list(data.get("embedding", []))
