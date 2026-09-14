"use client";

import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Droplets,
  Fish,
  Leaf,
  MessageCircle,
  Send,
  ShieldCheck,
  Sparkles,
  Waves,
} from "lucide-react";
import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type User = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farm_count: number;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi, I'm Aqua AI. You can ask me anything about aquaculture. You do not need to create a farm or provide farm details to start.",
    },
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadSession() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (!active) {
          return;
        }

        if (response.ok) {
          const data = (await response.json()) as User;
          setUser(data);
        }
      } catch {
      } finally {
        if (active) {
          setCheckingAuth(false);
        }
      }
    }

    loadSession();

    return () => {
      active = false;
    };
  }, []);

  async function sendMessage(textOverride?: string) {
    const text = (textOverride ?? input).trim();

    if (!text || chatLoading) {
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

    setChatLoading(true);

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
            "I could not answer that right now.",
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Aqua AI is temporarily unavailable. Please try again.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  function signIn() {
    window.location.href =
      `${API_URL}/api/v1/auth/google`;
  }

  function openFarmSetup() {
    const element =
      document.getElementById("farm-setup");

    element?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <a
            href="#top"
            className="flex items-center gap-3"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
              <Waves className="h-5 w-5" />
            </div>

            <div>
              <p className="text-sm font-bold tracking-tight">
                AquaLife
              </p>

              <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Aquaculture intelligence
              </p>
            </div>
          </a>

          <nav className="hidden items-center gap-6 text-xs font-medium text-muted-foreground md:flex">
            <a href="#ai" className="hover:text-foreground">
              Aqua AI
            </a>

            <a href="#platform" className="hover:text-foreground">
              Platform
            </a>

            <a href="#farm-setup" className="hover:text-foreground">
              Farm setup
            </a>
          </nav>

          <div className="flex items-center gap-2">
            {checkingAuth ? (
              <div className="h-9 w-24 animate-pulse rounded-xl bg-muted" />
            ) : user ? (
              <div className="flex items-center gap-2">
                <span className="hidden text-xs font-semibold sm:inline">
                  {user.full_name ?? user.email}
                </span>

                <button
                  type="button"
                  onClick={openFarmSetup}
                  className="rounded-xl bg-foreground px-3.5 py-2 text-xs font-semibold text-background"
                >
                  {user.farm_count > 0
                    ? "Manage farms"
                    : "Set up a farm"}
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={signIn}
                className="rounded-xl bg-foreground px-3.5 py-2 text-xs font-semibold text-background"
              >
                Sign in
              </button>
            )}
          </div>
        </div>
      </header>

      <section id="top" className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-0 h-[520px] w-[760px] -translate-x-1/2 rounded-full bg-foreground/[0.035] blur-3xl" />
        </div>

        <div className="relative mx-auto grid max-w-7xl gap-14 px-4 pb-16 pt-16 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-24 lg:pt-24">
          <div className="max-w-3xl self-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-foreground" />
              Built for modern aquaculture
            </div>

            <h1 className="mt-7 text-5xl font-bold tracking-[-0.05em] sm:text-6xl lg:text-7xl">
              Your aquaculture
              <span className="block text-muted-foreground">
                intelligence layer.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
              Explore AquaLife before setting anything up. Ask
              Aqua AI questions, learn about aquaculture, and only
              provide farm information when you actually need
              farm-specific intelligence.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  document
                    .getElementById("ai")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    });
                }}
                className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-xs font-semibold text-background"
              >
                Ask Aqua AI
                <ArrowRight className="h-4 w-4" />
              </button>

              {!user && (
                <button
                  type="button"
                  onClick={signIn}
                  className="flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-xs font-semibold"
                >
                  Continue with Google
                  <ShieldCheck className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Guest AI available
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Farm setup optional
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Google sign-in
              </span>
            </div>
          </div>

          <div
            id="ai"
            className="rounded-[2rem] border border-border bg-card p-4 shadow-2xl shadow-black/5 sm:p-5"
          >
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-foreground text-background">
                  <BrainCircuit className="h-5 w-5" />
                </div>

                <div>
                  <p className="text-sm font-semibold">
                    Aqua AI
                  </p>

                  <p className="text-[10px] text-muted-foreground">
                    {user
                      ? "Connected to your AquaLife account"
                      : "Explore without creating a farm"}
                  </p>
                </div>
              </div>

              <Sparkles className="h-4 w-4 text-muted-foreground" />
            </div>

            <div className="flex min-h-[420px] flex-col">
              <div className="flex-1 space-y-4 overflow-y-auto py-5">
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
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                        <BrainCircuit className="h-4 w-4" />
                      </div>
                    )}

                    <div
                      className={[
                        "max-w-[82%] rounded-2xl px-4 py-3 text-xs leading-6",
                        message.role === "user"
                          ? "bg-foreground text-background"
                          : "bg-muted",
                      ].join(" ")}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}

                {chatLoading && (
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                      <BrainCircuit className="h-4 w-4 animate-pulse" />
                    </div>

                    <div className="rounded-2xl bg-muted px-4 py-3 text-xs text-muted-foreground">
                      Aqua AI is thinking...
                    </div>
                  </div>
                )}
              </div>

              <div className="border-t border-border pt-4">
                <div className="mb-3 flex flex-wrap gap-2">
                  {[
                    "What is good dissolved oxygen for shrimp?",
                    "How does pH affect shrimp?",
                    "How is biomass estimated?",
                  ].map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => sendMessage(question)}
                      className="rounded-full border border-border px-3 py-1.5 text-[10px] text-muted-foreground transition hover:bg-muted"
                    >
                      {question}
                    </button>
                  ))}
                </div>

                <div className="flex gap-2">
                  <input
                    value={input}
                    onChange={(event) =>
                      setInput(event.target.value)
                    }
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        sendMessage();
                      }
                    }}
                    placeholder="Ask an aquaculture question..."
                    className="h-11 min-w-0 flex-1 rounded-xl border border-border bg-background px-3 text-xs outline-none focus:ring-2 focus:ring-ring"
                  />

                  <button
                    type="button"
                    onClick={() => sendMessage()}
                    disabled={!input.trim() || chatLoading}
                    className="flex h-11 w-11 items-center justify-center rounded-xl bg-foreground text-background disabled:opacity-40"
                    aria-label="Send message"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="platform"
        className="border-y border-border bg-muted/20"
      >
        <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Platform
            </p>

            <h2 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
              Start with knowledge. Add farm context when you need it.
            </h2>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <PlatformCard
              icon={BrainCircuit}
              title="Ask first"
              text="Use Aqua AI without creating a pond, farm or account."
            />

            <PlatformCard
              icon={Waves}
              title="Configure later"
              text="Add farm and pond information only when you want personalized intelligence."
            />

            <PlatformCard
              icon={Droplets}
              title="Go deeper"
              text="Once configured, connect water quality, feeding, growth, health and harvest data."
            />
          </div>
        </div>
      </section>

      <section
        id="farm-setup"
        className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24"
      >
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Farm intelligence
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight">
              Your farm is optional.
              <span className="block text-muted-foreground">
                Your curiosity isn't.
              </span>
            </h2>

            <p className="mt-4 text-sm leading-6 text-muted-foreground">
              You can explore AquaLife as a visitor. When you want
              farm-specific recommendations, we'll collect only the
              information required for that task.
            </p>

            {!user && (
              <button
                type="button"
                onClick={signIn}
                className="mt-6 flex items-center gap-2 rounded-xl bg-foreground px-4 py-2.5 text-xs font-semibold text-background"
              >
                Sign in when you're ready
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="rounded-3xl border border-border bg-card p-5 shadow-sm sm:p-7">
            <div className="grid gap-3 sm:grid-cols-3">
              <SetupCard
                icon={Leaf}
                title="Farm"
                text="Name, location and production setup"
              />

              <SetupCard
                icon={Waves}
                title="Ponds"
                text="Area, depth, water source and species"
              />

              <SetupCard
                icon={Fish}
                title="Operations"
                text="Feeding, growth, health and harvest"
              />
            </div>

            <div className="mt-5 rounded-2xl border border-dashed border-border bg-muted/20 p-4">
              <div className="flex items-center gap-3">
                <MessageCircle className="h-4 w-4" />

                <div>
                  <p className="text-xs font-semibold">
                    Nothing to configure yet?
                  </p>

                  <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
                    That's fine. Keep using Aqua AI and configure
                    your farm later.
                  </p>
                </div>
              </div>
            </div>

            {user && (
              <button
                type="button"
                onClick={() => {
                  window.location.href =
                    "/onboarding";
                }}
                className="mt-5 flex items-center gap-2 rounded-xl bg-foreground px-4 py-2.5 text-xs font-semibold text-background"
              >
                {user.farm_count > 0
                  ? "Open farm setup"
                  : "Set up my farm"}
                <ChevronRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-[10px] text-muted-foreground sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
          <span>
            AquaLife - Intelligent aquaculture platform
          </span>

          <span>
            Explore freely. Configure when needed. Predict when ready.
          </span>
        </div>
      </footer>
    </main>
  );
}

function PlatformCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <Icon className="h-5 w-5" />

      <p className="mt-5 text-sm font-semibold">
        {title}
      </p>

      <p className="mt-2 text-xs leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}

function SetupCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-border p-4">
      <Icon className="h-4 w-4" />

      <p className="mt-4 text-xs font-semibold">
        {title}
      </p>

      <p className="mt-1 text-[10px] leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}
