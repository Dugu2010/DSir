import { useState } from "react";
import Cookies from "js-cookie";
import { apiClient } from "@/lib/axios";

export type Message = { role: "user" | "assistant"; content: string };

export function useAIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatting, setIsChatting] = useState(false);

  const sendMessage = async (input: string) => {
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setIsChatting(true);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    let token = Cookies.get("access_token");

    const doFetch = () =>
      fetch(`${apiBase}/ai/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages: [...messages, userMsg],
          temperature: 0.7,
          max_tokens: 1024,
        }),
      });

    try {
      let res = await doFetch();

      if (res.status === 401) {
        await apiClient.get("/auth/me");
        token = Cookies.get("access_token");
        res = await doFetch();
      }

      if (!res.ok) {
        throw new Error(`Stream request failed: ${res.status}`);
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder("utf-8");

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      if (!reader) {
        throw new Error("No response body");
      }

      let chunk = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        chunk += decoder.decode(value, { stream: true });
        const parts = chunk.split("\n\n");
        chunk = parts.pop() || "";

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const text = part.slice(6);
            if (text === "[DONE]") continue;
            setMessages((prev) => {
              const newMsgs = [...prev];
              const last = newMsgs[newMsgs.length - 1];
              last.content += text;
              return newMsgs;
            });
          }
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, the AI mentor is unavailable right now." },
      ]);
    } finally {
      setIsChatting(false);
    }
  };

  return { messages, setMessages, isChatting, sendMessage };
}
