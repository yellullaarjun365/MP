"use client";

import { useState } from "react";
import {
  ArrowLeft,
  BrainCircuit,
  Send,
  Sparkles,
  Waves,
} from "lucide-react";
import Link from "next/link";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function PublicAiPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi. I'm Aqua AI. Ask me anything about aquaculture, pond management, water quality, feeding, growth or production.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    const text = input.trim();

    if (!text || loading) {
      return;
    }

    setInput("");

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: text,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/public/ai/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: text,
          }),
        },
      );

      const data = await response.json();

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            data.answer ??
            data.detail ??
            "Aqua AI could not answer that request.",
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "I couldn't reach Aqua AI right now. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 sm:px-6 lg:px-8">
        <header className="flex h-16 items-center justify-between border-b border-border">
          <Link
            href="/login"
            className="flex items-center gap-2 text-xs font-semibold"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to AquaLife
          </Link>

          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-foreground text-background">
              <Waves className="h-4 w-4" />
            </div>

            <span className="text-sm font-bold">
              Aqua AI
            </span>
          </div>

          <Link
            href="/login"
            className="rounded-xl border border-border px-3 py-2 text-[11px] font-semibold"
          >
            Sign in
          </Link>
        </header>

        <section className="mx-auto flex w-full max-w-4xl flex-1 flex-col py-8 sm:py-12">
          <div className="mb-8 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-foreground text-background">
              <BrainCircuit className="h-6 w-6" />
            </div>

            <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              Public AI assistant
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Ask Aqua anything about aquaculture.
            </h1>

            <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
              Explore AquaLife's aquaculture intelligence before
              creating a farm or connecting your account.
            </p>
          </div>

          <div className="flex-1 rounded-3xl border border-border bg-card p-4 shadow-sm sm:p-6">
            <div className="min-h-[420px] space-y-5">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={[
                    "flex gap-3",
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start",
                  ].join(" ")}
                >
                  {message.role === "assistant" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-foreground text-background">
                      <Sparkles className="h-4 w-4" />
                    </div>
                  )}

                  <div
                    className={[
                      "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-6",
                      message.role === "user"
                        ? "bg-foreground text-background"
                        : "bg-muted text-foreground",
                    ].join(" ")}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-foreground text-background">
                    <Sparkles className="h-4 w-4 animate-pulse" />
                  </div>

                  <div className="rounded-2xl bg-muted px-4 py-3 text-sm text-muted-foreground">
                    Aqua AI is thinking...
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex gap-2 border-t border-border pt-5">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    sendMessage();
                  }
                }}
                placeholder="Ask an aquaculture question..."
                className="h-12 min-w-0 flex-1 rounded-xl border border-border bg-background px-4 text-sm outline-none focus:ring-2 focus:ring-ring"
              />

              <button
                type="button"
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="flex h-12 items-center gap-2 rounded-xl bg-foreground px-5 text-xs font-semibold text-background disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Send className="h-4 w-4" />
                Send
              </button>
            </div>
          </div>

          <p className="mt-4 text-center text-[10px] text-muted-foreground">
            Guest mode provides general aquaculture information.
            Farm-specific intelligence becomes available after sign in.
          </p>
        </section>
      </div>
    </main>
  );
}
