"use client";

import { useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Send,
  Waves,
} from "lucide-react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export function PublicAiPreview() {
  const [message, setMessage] = useState("");

  function askAqua() {
    window.location.href = "/ai";
  }

  return (
    <div className="rounded-3xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-foreground text-background">
          <BrainCircuit className="h-5 w-5" />
        </div>

        <div>
          <p className="text-sm font-semibold">
            Ask Aqua AI
          </p>

          <p className="text-[11px] text-muted-foreground">
            No account required to explore
          </p>
        </div>
      </div>

      <div className="mt-5 rounded-2xl border border-border bg-muted/20 p-4">
        <p className="text-[11px] text-muted-foreground">
          Try asking:
        </p>

        <div className="mt-3 flex flex-wrap gap-2">
          {[
            "What is good dissolved oxygen for shrimp?",
            "How does pH affect aquaculture?",
            "Explain biomass estimation",
          ].map((question) => (
            <button
              key={question}
              type="button"
              onClick={() => setMessage(question)}
              className="rounded-full border border-border px-3 py-1.5 text-[10px] transition hover:bg-muted"
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <div className="flex min-w-0 flex-1 items-center rounded-xl border border-border bg-background px-3">
          <Waves className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />

          <input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask an aquaculture question..."
            className="h-11 min-w-0 flex-1 bg-transparent text-xs outline-none placeholder:text-muted-foreground"
          />
        </div>

        <button
          type="button"
          onClick={askAqua}
          className="flex h-11 items-center gap-2 rounded-xl bg-foreground px-4 text-xs font-semibold text-background"
        >
          <Send className="h-4 w-4" />
          Ask
        </button>
      </div>

      <button
        type="button"
        onClick={askAqua}
        className="mt-4 flex items-center gap-2 text-xs font-semibold"
      >
        Explore Aqua AI
        <ArrowRight className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
