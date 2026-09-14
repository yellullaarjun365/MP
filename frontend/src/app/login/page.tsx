"use client";

import {
  Activity,
  ArrowRight,
  BrainCircuit,
  Droplets,
  Fish,
  Moon,
  ShieldCheck,
  Sun,
  Waves,
} from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function LoginPage() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const dark = resolvedTheme === "dark";
  const googleLoginUrl = `${API_URL}/api/v1/auth/google`;

  return (
    <main className="min-h-screen overflow-hidden bg-background">
      <div className="relative min-h-screen">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -right-40 -top-40 h-[520px] w-[520px] rounded-full bg-foreground/[0.035] blur-3xl" />
          <div className="absolute -bottom-40 -left-40 h-[520px] w-[520px] rounded-full bg-foreground/[0.025] blur-3xl" />
        </div>

        <header className="relative z-10 flex h-20 items-center justify-between px-6 sm:px-10 lg:px-14">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-foreground text-background shadow-sm">
              <Waves className="h-5 w-5" />
            </div>

            <div>
              <div className="text-sm font-bold tracking-tight">
                AquaLife
              </div>

              <div className="text-[9px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                Aquaculture intelligence
              </div>
            </div>
          </div>

          {mounted && (
            <button
              type="button"
              onClick={() => setTheme(dark ? "light" : "dark")}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-background/70 transition hover:bg-muted"
              aria-label="Toggle theme"
            >
              {dark ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
          )}
        </header>

        <section className="relative z-10 mx-auto grid min-h-[calc(100vh-5rem)] max-w-7xl items-center gap-16 px-6 pb-16 pt-8 sm:px-10 lg:grid-cols-[1.05fr_0.95fr] lg:px-14 lg:pt-0">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-foreground" />
              Intelligent aquaculture
            </div>

            <h1 className="mt-7 text-5xl font-bold leading-[1.02] tracking-[-0.045em] sm:text-6xl lg:text-7xl">
              Run your farms with
              <span className="block text-muted-foreground">
                intelligence.
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-base leading-7 text-muted-foreground sm:text-lg">
              AquaLife brings farm operations, pond monitoring,
              production analytics and AI-assisted decision making
              into one command center.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:max-w-sm">
              <a
                href={googleLoginUrl}
                className="group flex h-12 items-center justify-center gap-3 rounded-xl bg-foreground px-5 text-sm font-semibold text-background shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <span className="flex h-6 w-6 items-center justify-center rounded-md bg-background text-xs font-bold text-foreground">
                  G
                </span>

                Continue with Google

                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </a>

              <div className="flex items-center justify-center gap-2 text-[11px] text-muted-foreground">
                <ShieldCheck className="h-3.5 w-3.5" />
                Secure authentication
              </div>
            </div>

            <div className="mt-10 grid max-w-xl grid-cols-3 gap-6 border-t border-border pt-6">
              <Feature
                icon={Droplets}
                title="Monitor"
                text="Water quality"
              />

              <Feature
                icon={Activity}
                title="Understand"
                text="Production data"
              />

              <Feature
                icon={BrainCircuit}
                title="Predict"
                text="AI intelligence"
              />
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-8 rounded-[3rem] bg-foreground/[0.025] blur-2xl" />

            <div className="relative overflow-hidden rounded-[2rem] border border-border bg-card p-5 shadow-2xl shadow-black/5 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Live command center
                  </p>

                  <p className="mt-2 text-lg font-bold tracking-tight">
                    Primary Farm
                  </p>
                </div>

                <div className="flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-[10px] font-semibold">
                  <span className="h-1.5 w-1.5 rounded-full bg-foreground" />
                  Healthy
                </div>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-3">
                <MiniMetric
                  label="Biomass"
                  value="3.9 t"
                  change="+8.4%"
                />

                <MiniMetric
                  label="Survival"
                  value="94.2%"
                  change="+1.8%"
                />
              </div>

              <div className="mt-4 rounded-2xl border border-border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold">
                      Pond health
                    </p>

                    <p className="mt-1 text-[10px] text-muted-foreground">
                      Latest observations
                    </p>
                  </div>

                  <Fish className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="mt-5 space-y-3">
                  <PondRow
                    name="Pond 01"
                    species="Vannamei"
                    value="5.4 mg/L"
                  />

                  <PondRow
                    name="Pond 02"
                    species="Vannamei"
                    value="6.1 mg/L"
                  />

                  <PondRow
                    name="Pond 03"
                    species="Vannamei"
                    value="4.8 mg/L"
                  />
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-border bg-muted/30 p-4">
                <div className="flex gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-foreground text-background">
                    <BrainCircuit className="h-4 w-4" />
                  </div>

                  <div>
                    <p className="text-xs font-semibold">
                      Aqua AI
                    </p>

                    <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
                      Pond 03 may need attention. Recent dissolved
                      oxygen readings are trending below the farm's
                      recent baseline.
                    </p>

                    <button
                      type="button"
                      className="mt-3 text-[10px] font-semibold underline underline-offset-4"
                    >
                      Review insight
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function Feature({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div>
      <Icon className="h-4 w-4" />

      <p className="mt-3 text-xs font-semibold">
        {title}
      </p>

      <p className="mt-1 text-[10px] text-muted-foreground">
        {text}
      </p>
    </div>
  );
}

function MiniMetric({
  label,
  value,
  change,
}: {
  label: string;
  value: string;
  change: string;
}) {
  return (
    <div className="rounded-2xl border border-border p-4">
      <p className="text-[10px] text-muted-foreground">
        {label}
      </p>

      <div className="mt-2 flex items-end justify-between gap-2">
        <span className="text-xl font-bold tracking-tight">
          {value}
        </span>

        <span className="text-[10px] font-semibold">
          {change}
        </span>
      </div>
    </div>
  );
}

function PondRow({
  name,
  species,
  value,
}: {
  name: string;
  species: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
          <Waves className="h-3.5 w-3.5" />
        </div>

        <div>
          <p className="text-[11px] font-semibold">
            {name}
          </p>

          <p className="text-[9px] text-muted-foreground">
            {species}
          </p>
        </div>
      </div>

      <span className="text-[10px] font-semibold">
        {value}
      </span>
    </div>
  );
}
