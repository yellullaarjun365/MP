"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  Clock3,
  Database,
  Fingerprint,
  Info,
  ShieldCheck,
} from "lucide-react";


type ModelState =
  | "VERIFIED"
  | "PENDING";


type FarmResult = {
  rmse_mg_l: number;
  horizon_hours: number;
  horizon_steps: number;
  interval_minutes: number;
  status: string;
};


type ModelResult = {
  state: ModelState;
  fleet_rmse_mg_l: number | null;
  farms: Record<
    string,
    FarmResult
  >;
  report_sha256: string | null;
  report_path: string;
};


type BenchmarkData = {
  schema_version: string;
  generated_at_utc: string;

  task: {
    id: number;
    name: string;
    target: string;
    target_unit: string;
    metric: string;
    horizon_hours: number;
    interval_minutes: number;
    horizon_steps: number;
    farms: string[];
  };

  models: Record<
    string,
    ModelResult
  >;

  scientific_boundary: {
    public_data_only: boolean;
    commercial_12_farm_validation: boolean;
    real_world_validation: boolean;
    production_accuracy_claim: boolean;
    automatic_model_ranking: boolean;
  };

  status: string;
};


const MODEL_ORDER = [
  "Persistence",
  "XGBoost",
  "Random Forest",
  "LSTM",
];


const FEATURES = [
  {
    name: "DO_lag_15m",
    description:
      "Historical dissolved oxygen value 15 minutes before forecast origin.",
  },
  {
    name: "DO_lag_60m",
    description:
      "Historical dissolved oxygen value 60 minutes before forecast origin.",
  },
  {
    name: "DO_lag_3h",
    description:
      "Historical dissolved oxygen value 3 hours before forecast origin.",
  },
  {
    name: "DO_lag_6h",
    description:
      "Historical dissolved oxygen value 6 hours before forecast origin.",
  },
  {
    name: "DO_lag_24h",
    description:
      "Historical dissolved oxygen value 24 hours before forecast origin.",
  },
  {
    name: "DO_lag_72h",
    description:
      "Historical dissolved oxygen value 72 hours before forecast origin.",
  },
];


function slugify(
  value: string,
) {
  return value
    .toLowerCase()
    .replace(/\s+/g, "-");
}


export default function ModelDetailPage({
  params,
}: {
  params: Promise<{
    model: string;
  }>;
}) {

  const [slug, setSlug] =
    useState<string | null>(null);

  const [data, setData] =
    useState<BenchmarkData | null>(null);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

        const resolved =
          await params;

        const response =
          await fetch(
            "/data/model-benchmark.json",
            {
              cache: "no-store",
            },
          );

        if (!response.ok) {
          throw new Error(
            `HTTP ${response.status}`,
          );
        }

        const result =
          (await response.json()) as BenchmarkData;

        if (cancelled) {
          return;
        }

        setSlug(
          decodeURIComponent(
            resolved.model,
          ),
        );

        setData(
          result,
        );

      } catch {

        if (!cancelled) {

          setError(
            "Unable to load model details.",
          );
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };

  }, [params]);


  if (error) {

    return (
      <div className="w-full">

        <div className="mx-auto max-w-[1500px] px-4 py-8 sm:px-6 lg:px-8">

          <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6 text-sm text-destructive">
            {error}
          </div>

        </div>

      </div>
    );
  }


  if (!data || !slug) {

    return (
      <div className="w-full">

        <div className="mx-auto max-w-[1500px] px-4 py-8 sm:px-6 lg:px-8">

          <div className="rounded-2xl border border-border bg-card p-8 text-center">

            <p className="text-sm font-semibold">
              Loading model details
            </p>

            <p className="mt-2 text-xs text-muted-foreground">
              Loading verified Task-1 benchmark metadata.
            </p>

          </div>

        </div>

      </div>
    );
  }


  const modelName =
    MODEL_ORDER.find(
      (name) =>
        slugify(name) === slug,
    ) ?? slug;


  const model =
    data.models[modelName];


  if (!model) {

    return (
      <div className="w-full">

        <div className="mx-auto max-w-[1500px] px-4 py-8 sm:px-6 lg:px-8">

          <div className="rounded-2xl border border-border bg-card p-6">

            <p className="text-sm font-semibold">
              Model not found
            </p>

            <p className="mt-2 text-xs text-muted-foreground">
              No benchmark record exists for:
              {" "}
              {slug}
            </p>

            <Link
              href="/models"
              className="mt-5 inline-flex items-center gap-2 rounded-xl border border-border px-4 py-2.5 text-xs font-semibold hover:bg-muted"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to models
            </Link>

          </div>

        </div>

      </div>
    );
  }


  const verified =
    model.state === "VERIFIED";


  const explanationTitle =
    modelName === "Persistence"
      ? "Rule-based explanation"
      : "Numerical attribution pending";


  const explanationText =
    modelName === "Persistence"
      ? "The persistence result follows its explicit prediction rule."
      : "Numerical feature attribution requires the dedicated controlled analysis and is not inferred from the benchmark score.";


  return (
    <div className="w-full">

      <div className="mx-auto w-full max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">

        <div className="flex flex-col gap-6">


          <Link
            href="/models"
            className="inline-flex w-fit items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to model benchmark
          </Link>


          {/* HERO */}

          <section className="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-8">

            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">

              <div>

                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">

                  <BarChart3 className="h-4 w-4" />

                  Model intelligence

                </div>


                <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
                  {modelName}
                </h1>


                <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
                  AquaLife Task-1 model evaluation and
                  provenance details for the public benchmark.
                </p>

              </div>


              <div
                className="inline-flex w-fit items-center gap-2 rounded-full border border-border px-3 py-2 text-xs font-semibold"
              >

                {verified ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Clock3 className="h-4 w-4" />
                )}

                {verified
                  ? "Verified benchmark"
                  : "Benchmark pending"}

              </div>

            </div>


            <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <Metric
                label="Fleet RMSE"
                value={
                  model.fleet_rmse_mg_l === null
                    ? "—"
                    : model.fleet_rmse_mg_l.toFixed(4)
                }
                suffix={
                  model.fleet_rmse_mg_l === null
                    ? undefined
                    : "mg/L"
                }
              />


              <Metric
                label="Forecast horizon"
                value={
                  `${data.task.horizon_hours}`
                }
                suffix="hours"
              />


              <Metric
                label="Sampling interval"
                value={
                  `${data.task.interval_minutes}`
                }
                suffix="minutes"
              />


              <Metric
                label="Forecast steps"
                value={
                  `${data.task.horizon_steps}`
                }
              />

            </div>

          </section>


          {/* FARM RESULTS */}

          <section className="rounded-2xl border border-border bg-card shadow-sm">

            <div className="border-b border-border p-5">

              <p className="text-sm font-semibold">
                Farm-level evaluation
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Independent public-data measurements under the
                common 72-hour Task-1 protocol.
              </p>

            </div>


            <div className="overflow-x-auto">

              <table className="w-full min-w-[650px] text-sm">

                <thead>

                  <tr className="border-b border-border text-left text-xs text-muted-foreground">

                    <th className="px-5 py-4 font-medium">
                      Farm
                    </th>

                    <th className="px-5 py-4 font-medium">
                      RMSE
                    </th>

                    <th className="px-5 py-4 font-medium">
                      Horizon
                    </th>

                    <th className="px-5 py-4 font-medium">
                      Interval
                    </th>

                    <th className="px-5 py-4 font-medium">
                      Status
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {data.task.farms.map(
                    (farmId) => {

                      const result =
                        model.farms[farmId] ??
                        null;

                      return (
                        <tr
                          key={farmId}
                          className="border-b border-border last:border-0"
                        >

                          <td className="px-5 py-4 font-semibold">
                            {farmId}
                          </td>

                          <td className="px-5 py-4 font-medium">

                            {result
                              ? `${result.rmse_mg_l.toFixed(4)} mg/L`
                              : "Pending"}

                          </td>

                          <td className="px-5 py-4 text-xs text-muted-foreground">

                            {result
                              ? `${result.horizon_hours}h / ${result.horizon_steps} steps`
                              : "—"}

                          </td>

                          <td className="px-5 py-4 text-xs text-muted-foreground">

                            {result
                              ? `${result.interval_minutes}m`
                              : "—"}

                          </td>

                          <td className="px-5 py-4">

                            {result ? (
                              <span className="inline-flex items-center gap-1.5 text-xs font-semibold">
                                <CheckCircle2 className="h-3.5 w-3.5" />
                                Verified
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                                <Clock3 className="h-3.5 w-3.5" />
                                Pending
                              </span>
                            )}

                          </td>

                        </tr>
                      );

                    },
                  )}

                </tbody>

              </table>

            </div>

          </section>


          <div className="grid gap-6 lg:grid-cols-2">


            {/* EXPLANATION */}

            <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <Info className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Prediction explanation
                </p>

              </div>


              <p className="mt-5 text-sm font-semibold">
                {explanationTitle}
              </p>


              <p className="mt-2 text-xs leading-5 text-muted-foreground">
                {explanationText}
              </p>


              <div className="mt-5 rounded-xl border border-border bg-muted/20 p-4">

                <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
                  Interpretation boundary
                </p>

                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  Feature importance describes model behavior.
                  It does not establish that a feature caused the
                  predicted water-quality value.
                </p>

              </div>

            </section>


            {/* PROTOCOL */}

            <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <Database className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Evaluation protocol
                </p>

              </div>


              <div className="mt-5 space-y-3">

                <ProtocolRow
                  label="Benchmark"
                  value="AquaSustain-Bench"
                />

                <ProtocolRow
                  label="Task"
                  value="Task 1 — Water Quality Forecasting"
                />

                <ProtocolRow
                  label="Target"
                  value={`${data.task.target} (${data.task.target_unit})`}
                />

                <ProtocolRow
                  label="Metric"
                  value={data.task.metric}
                />

                <ProtocolRow
                  label="Data scope"
                  value="A1 / B1 / C1 public samples"
                />

              </div>

            </section>

          </div>


          {/* FEATURE CONTRACT */}

          {modelName !== "Persistence" && (

            <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <Database className="h-4 w-4" />

                <div>

                  <p className="text-sm font-semibold">
                    Input feature contract
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    Historical dissolved-oxygen features associated
                    with the tree-model evaluation.
                  </p>

                </div>

              </div>


              <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">

                {FEATURES.map(
                  (feature) => (

                    <div
                      key={feature.name}
                      className="rounded-xl border border-border bg-muted/20 p-4"
                    >

                      <p className="font-mono text-xs font-semibold">
                        {feature.name}
                      </p>

                      <p className="mt-2 text-xs leading-5 text-muted-foreground">
                        {feature.description}
                      </p>

                    </div>

                  ),
                )}

              </div>

            </section>

          )}


          {/* PROVENANCE */}

          <section className="grid gap-6 lg:grid-cols-2">

            <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <Fingerprint className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Provenance
                </p>

              </div>


              <div className="mt-5 space-y-4">

                <Provenance
                  label="Source artifact"
                  value={
                    model.report_path
                  }
                />

                <Provenance
                  label="SHA-256"
                  value={
                    model.report_sha256 ??
                    "Pending"
                  }
                  mono
                />

                <Provenance
                  label="UI dataset"
                  value="public/data/model-benchmark.json"
                />

                <Provenance
                  label="Generated"
                  value={
                    data.generated_at_utc
                  }
                />

              </div>

            </div>


            <div className="rounded-2xl border border-border bg-muted/20 p-5">

              <div className="flex items-center gap-2">

                <ShieldCheck className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Validation boundaries
                </p>

              </div>


              <div className="mt-5 space-y-3">

                <Boundary
                  label="Commercial 12-farm validation"
                  value={
                    data.scientific_boundary
                      .commercial_12_farm_validation
                  }
                />

                <Boundary
                  label="Real-world validation"
                  value={
                    data.scientific_boundary
                      .real_world_validation
                  }
                />

                <Boundary
                  label="Production accuracy claim"
                  value={
                    data.scientific_boundary
                      .production_accuracy_claim
                  }
                />

                <Boundary
                  label="Automatic model ranking"
                  value={
                    data.scientific_boundary
                      .automatic_model_ranking
                  }
                />

              </div>

            </div>

          </section>


          <section className="rounded-2xl border border-border bg-muted/20 p-5">

            <div className="flex items-start gap-3">

              <Clock3 className="mt-0.5 h-4 w-4" />

              <div>

                <p className="text-sm font-semibold">
                  Benchmark context
                </p>

                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                  This page presents offline public-benchmark
                  measurements. It is not a commercial validation
                  dashboard and does not authorize autonomous farm
                  actions.
                </p>

              </div>

            </div>

          </section>

        </div>

      </div>

    </div>
  );
}


function Metric({
  label,
  value,
  suffix,
}: {
  label: string;
  value: string;
  suffix?: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-muted/20 p-4">

      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold tracking-tight">

        {value}

        {suffix && (
          <span className="ml-1 text-xs font-normal text-muted-foreground">
            {suffix}
          </span>
        )}

      </p>

    </div>
  );
}


function ProtocolRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-5 border-b border-border pb-3 last:border-0 last:pb-0">

      <span className="text-xs text-muted-foreground">
        {label}
      </span>

      <span className="text-right text-xs font-semibold">
        {value}
      </span>

    </div>
  );
}


function Provenance({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="border-b border-border pb-3 last:border-0 last:pb-0">

      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
        {label}
      </p>

      <p
        className={[
          "mt-1 break-all text-xs",
          mono ? "font-mono" : "",
        ].join(" ")}
      >
        {value}
      </p>

    </div>
  );
}


function Boundary({
  label,
  value,
}: {
  label: string;
  value: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-border bg-background p-3">

      <span className="text-xs text-muted-foreground">
        {label}
      </span>

      <span className="shrink-0 text-[10px] font-semibold">
        {value
          ? "PERFORMED"
          : "NOT PERFORMED"}
      </span>

    </div>
  );
}