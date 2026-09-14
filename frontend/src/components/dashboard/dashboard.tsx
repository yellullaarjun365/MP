"use client";

import {
  Activity,
  BarChart3,
  BrainCircuit,
  Droplets,
  Fish,
  Gauge,
  LayoutDashboard,
  Settings,
  Waves,
} from "lucide-react";

import { ThemeToggle } from "@/components/theme/theme-toggle";

const navSections = [
  {
    title: "Overview",
    items: [
      { label: "Dashboard", icon: LayoutDashboard, active: true },
      { label: "Farms", icon: Waves },
      { label: "Ponds", icon: Gauge },
    ],
  },
  {
    title: "Operations",
    items: [
      { label: "Water Quality", icon: Droplets },
      { label: "Feeding", icon: Fish },
      { label: "Growth", icon: BarChart3 },
    ],
  },
  {
    title: "Intelligence",
    items: [
      { label: "Analytics", icon: BarChart3 },
      { label: "Forecasts", icon: Gauge },
      { label: "Aqua AI", icon: BrainCircuit },
    ],
  },
];

export function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="min-w-0 flex-1">
          <Header />

          <main className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <DashboardContent />
          </main>
        </div>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-border/70 bg-background lg:flex lg:flex-col">
      <div className="flex h-16 items-center border-b border-border/70 px-5">
        <div className="flex items-center gap-2.5">
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
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-5">
        <div className="space-y-7">
          {navSections.map((section) => (
            <div key={section.title}>
              <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {section.title}
              </p>

              <div className="mt-2 space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;

                  return (
                    <button
                      key={item.label}
                      type="button"
                      className={[
                        "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition",
                        item.active
                          ? "bg-muted font-semibold"
                          : "text-muted-foreground hover:bg-muted/70 hover:text-foreground",
                      ].join(" ")}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>

                      {item.label === "Aqua AI" && (
                        <span className="ml-auto rounded-full border border-border px-1.5 py-0.5 text-[9px] font-semibold">
                          AI
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          <div>
            <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              System
            </p>

            <button
              type="button"
              className="mt-2 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
          </div>
        </div>
      </div>

      <div className="border-t border-border/70 p-4">
        <div className="rounded-2xl border border-border bg-muted/30 p-3">
          <p className="text-xs font-semibold">
            Aqua AI
          </p>

          <p className="mt-1 text-[11px] leading-4 text-muted-foreground">
            Ask questions about your farms, ponds and production data.
          </p>

          <button
            type="button"
            className="mt-3 w-full rounded-lg bg-foreground px-3 py-2 text-xs font-semibold text-background transition hover:opacity-90"
          >
            Ask Aqua
          </button>
        </div>
      </div>
    </aside>
  );
}

function Header() {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-border/70 bg-background/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <div className="lg:hidden">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
            <Waves className="h-5 w-5" />
          </div>
        </div>

        <div className="hidden sm:block">
          <p className="text-xs text-muted-foreground">
            Workspace
          </p>
          <p className="text-sm font-semibold">
            Primary Farm
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          className="hidden h-9 items-center gap-2 rounded-xl border border-border bg-muted/30 px-3 text-xs text-muted-foreground transition hover:bg-muted sm:flex"
        >
          <span>Search</span>
          <span className="rounded-md border border-border bg-background px-1.5 py-0.5 text-[9px]">
            Ctrl K
          </span>
        </button>

        <ThemeToggle />

        <button
          type="button"
          className="flex items-center gap-2 rounded-full border border-border px-2 py-1.5"
        >
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-background">
            A
          </span>

          <span className="hidden pr-2 text-xs font-semibold md:inline">
            Arjun
          </span>
        </button>
      </div>
    </header>
  );
}

function DashboardContent() {
  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Command center
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Good evening, Arjun.
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            Here's what needs your attention across your aquaculture
            operation today.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            className="rounded-xl border border-border px-4 py-2.5 text-xs font-semibold transition hover:bg-muted"
          >
            Export report
          </button>

          <button
            type="button"
            className="rounded-xl bg-foreground px-4 py-2.5 text-xs font-semibold text-background transition hover:opacity-90"
          >
            Add record
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="Estimated biomass"
          value="12.8 t"
          delta="+8.4%"
          description="Across 8 active ponds"
          icon={Activity}
        />

        <Metric
          label="Survival rate"
          value="94.2%"
          delta="+1.8%"
          description="Compared with previous cycle"
          icon={Fish}
        />

        <Metric
          label="Water quality"
          value="Good"
          delta="92%"
          description="Based on latest observations"
          icon={Droplets}
        />

        <Metric
          label="Active ponds"
          value="8"
          delta="6 normal"
          description="2 currently need attention"
          icon={Gauge}
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">
        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold">
                Production trajectory
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Estimated biomass across your operation
              </p>
            </div>

            <button
              type="button"
              className="rounded-lg border border-border px-3 py-1.5 text-[10px] font-semibold"
            >
              30 days
            </button>
          </div>

          <div className="mt-6 h-64 rounded-xl bg-muted/30 p-5">
            <div className="flex h-full items-end gap-2">
              {[24, 31, 28, 38, 44, 41, 50, 58, 61, 68, 73, 82].map(
                (height, index) => (
                  <div
                    key={index}
                    className="flex-1 rounded-t-md bg-foreground/75"
                    style={{ height: `${height}%` }}
                  />
                ),
              )}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
          <p className="text-sm font-semibold">
            Aqua AI insights
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Signals from recent pond activity
          </p>

          <div className="mt-5 space-y-3">
            <Insight
              title="Pond 03 deserves attention"
              text="Dissolved oxygen is trending below its recent farm baseline."
            />

            <Insight
              title="Feeding efficiency improving"
              text="Recent feed usage is trending below the previous cycle."
            />

            <Insight
              title="Growth looks on track"
              text="Recent sampling is consistent with the expected trajectory."
            />
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-end justify-between">
          <div>
            <p className="text-sm font-semibold">
              Farms
            </p>

            <p className="mt-1 text-xs text-muted-foreground">
              Current operating status
            </p>
          </div>

          <button
            type="button"
            className="text-xs font-semibold underline underline-offset-4"
          >
            View all
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <FarmCard
            name="AquaLife Primary Farm"
            location="Andhra Pradesh"
            species="Vannamei Shrimp"
            ponds="2 ponds"
            biomass="3.9 t"
            status="Healthy"
          />

          <FarmCard
            name="Research & Demo Farm"
            location="Andhra Pradesh"
            species="Vannamei Shrimp"
            ponds="6 ponds"
            biomass="8.9 t"
            status="Attention"
          />
        </div>
      </section>
    </div>
  );
}

function Metric({
  label,
  value,
  delta,
  description,
  icon: Icon,
}: {
  label: string;
  value: string;
  delta: string;
  description: string;
  icon: typeof Activity;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-muted-foreground">
            {label}
          </p>

          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight">
              {value}
            </span>

            <span className="text-[10px] font-semibold text-muted-foreground">
              {delta}
            </span>
          </div>
        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-muted">
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <p className="mt-3 text-[11px] leading-4 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function Insight({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex gap-3">
        <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-foreground" />

        <div>
          <p className="text-xs font-semibold">
            {title}
          </p>

          <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
            {text}
          </p>
        </div>
      </div>
    </div>
  );
}

function FarmCard({
  name,
  location,
  species,
  ponds,
  biomass,
  status,
}: {
  name: string;
  location: string;
  species: string;
  ponds: string;
  biomass: string;
  status: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-semibold">
            {name}
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            {location}
          </p>
        </div>

        <span className="rounded-full border border-border px-2.5 py-1 text-[10px] font-semibold">
          {status}
        </span>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <Data
          label="Species"
          value={species}
        />

        <Data
          label="Ponds"
          value={ponds}
        />

        <Data
          label="Biomass"
          value={biomass}
        />
      </div>

      <div className="mt-5 border-t border-border pt-4">
        <button
          type="button"
          className="text-xs font-semibold"
        >
          Open farm →
        </button>
      </div>
    </div>
  );
}

function Data({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 text-xs font-semibold">
        {value}
      </p>
    </div>
  );
}
