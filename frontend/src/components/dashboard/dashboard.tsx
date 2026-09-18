"use client";

import { FaoVannameiHistory } from "./fao-vannamei-history";


import { useEffect, useState } from "react";
import Link from "next/link";

import type { Pond } from "@/lib/api/ponds";
import {
  listFarms,
  type Farm,
} from "@/lib/api/farms";

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
import { AquaAIDrawer, AquaAIButton } from "@/components/ai/aqua-ai-drawer";
import { ProductionPredictionCard } from "@/components/dashboard/production-prediction-card";
import { DashboardWaterQuality } from "./dashboard-water-quality";
import { DashboardModelStatus } from "./dashboard-model-status";
import { DashboardFarmContext } from "./dashboard-farm-context";

const navSections = [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        href: "/dashboard",
        icon: LayoutDashboard,
        active: true,
      },
      {
        label: "Farms",
        href: "/water-quality",
        icon: Waves,
      },
      {
        label: "Ponds",
        href: "/water-quality",
        icon: Gauge,
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        label: "Water Quality",
        href: "/water-quality",
        icon: Droplets,
      },
      {
        label: "Feeding",
        href: "/dashboard",
        icon: Fish,
      },
      {
        label: "Growth",
        href: "/dashboard",
        icon: BarChart3,
      },
    ],
  },
  {
    title: "Intelligence",
    items: [
      {
        label: "Analytics",
        href: "/models",
        icon: BarChart3,
      },
      {
        label: "Forecasts",
        href: "/forecast",
        icon: Gauge,
      },
      {
        label: "Aqua AI",
        href: "/ai",
        icon: BrainCircuit,
      },
    ],
  },
];

export function Dashboard() {
  return <DashboardContent />;
}

function DashboardContent() {

  return (
    <DashboardIntegratedContent />
  );

}


function DashboardIntegratedContent() {

  const [
    selectedPond,
    setSelectedPond,
  ] = useState<Pond | null>(null);


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
            Your AquaLife command center for farm operations,
            water quality, forecasting, and model intelligence.
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


      <DashboardFarmContext
        onPondChange={setSelectedPond}
      />


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <Metric
          label="Estimated biomass"
          value="12.8 t"
          delta="+8.4%"
          description="Current application estimate"
          icon={Activity}
        />

        <Metric
          label="Survival rate"
          value="94.2%"
          delta="+1.8%"
          description="Current application estimate"
          icon={Fish}
        />

        <Metric
          label="Water quality"
          value={
            selectedPond
              ? "Live"
              : "Select pond"
          }
          delta={
            selectedPond
              ? "Connected"
              : "Awaiting context"
          }
          description="Based on recorded observations"
          icon={Droplets}
        />

        <Metric
          label="Ponds"
          value={
            selectedPond
              ? "1 selected"
              : "None selected"
          }
          delta="Operational"
          description="Current dashboard context"
          icon={Gauge}
        />

      </section>


      <section className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">

        <DashboardWaterQuality
          pondId={
            selectedPond?.id ??
            null
          }
        />

        <DashboardModelStatus />

      </section>


      <ProductionPredictionCard />

      <FaoVannameiHistory />


      <section className="grid gap-4 xl:grid-cols-[1.65fr_1fr]">

        <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm font-semibold">
                Production trajectory
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Application production view
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
                    style={{
                      height: `${height}%`,
                    }}
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
            Insight layer
          </p>


          <div className="mt-5 space-y-3">

            <Insight
              title="Water quality data connected"
              text="Observed measurements are now available from the selected pond."
            />

            <Insight
              title="Model transparency available"
              text="Benchmark models can be inspected from the Models workspace."
            />

            <Insight
              title="Forecast workspace ready"
              text="Use the Forecasts workspace for observed history and future model output."
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

          <Link
            href="/water-quality"
            className="text-xs font-semibold underline underline-offset-4"
          >
            View operations
          </Link>

        </div>


                <DashboardFarmCards />

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

function DashboardFarmCards() {

  const [farms, setFarms] =
    useState<Farm[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

        const result =
          await listFarms();

        if (cancelled) {
          return;
        }

        setFarms(result);

      } catch {

        if (!cancelled) {
          setError(
            "Unable to load farms.",
          );
        }

      } finally {

        if (!cancelled) {
          setLoading(false);
        }

      }
    }

    void load();

    return () => {
      cancelled = true;
    };

  }, []);


  if (loading) {

    return (
      <div className="grid gap-4 md:grid-cols-2">

        <div className="h-44 animate-pulse rounded-2xl border border-border bg-muted/30" />

        <div className="h-44 animate-pulse rounded-2xl border border-border bg-muted/30" />

      </div>
    );

  }


  if (error) {

    return (
      <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6">

        <p className="text-sm font-semibold">
          Farm data unavailable
        </p>

        <p className="mt-2 text-xs text-destructive/80">
          {error}
        </p>

      </div>
    );

  }


  if (farms.length === 0) {

    return (
      <div className="rounded-2xl border border-dashed border-border p-8 text-center">

        <p className="text-sm font-semibold">
          No farms found
        </p>

        <p className="mt-2 text-xs text-muted-foreground">
          Create a farm to begin using the AquaLife dashboard.
        </p>

      </div>
    );

  }


  return (
    <div className="grid gap-4 md:grid-cols-2">

      {farms.map(
        (farm) => (
          <LiveFarmCard
            key={farm.id}
            farm={farm}
          />
        ),
      )}

    </div>
  );
}


function LiveFarmCard({
  farm,
}: {
  farm: Farm;
}) {

  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">

      <div className="flex items-start justify-between gap-4">

        <div className="min-w-0">

          <p className="truncate text-sm font-semibold">
            {farm.name}
          </p>

          <p className="mt-1 truncate text-xs text-muted-foreground">
            {farm.location ??
              "Location not specified"}
          </p>

        </div>

        <span className="shrink-0 rounded-full border border-border px-2.5 py-1 text-[10px] font-semibold">
          Connected
        </span>

      </div>


      <div className="mt-6 grid grid-cols-3 gap-4">

        <Data
          label="Type"
          value={
            farm.farm_type ??
            "Not specified"
          }
        />

        <Data
          label="Area"
          value={
            farm.total_area_m2 !== null
              ? `${farm.total_area_m2} m²`
              : "Not specified"
          }
        />

        <Data
          label="Water"
          value={
            farm.water_source ??
            "Not specified"
          }
        />

      </div>


      <div className="mt-5 border-t border-border pt-4">

        <Link
          href="/water-quality"
          className="text-xs font-semibold"
        >
          Open farm →
        </Link>

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