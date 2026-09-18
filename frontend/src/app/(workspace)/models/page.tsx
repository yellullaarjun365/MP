"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock3,
  Database,
  ShieldCheck,
} from "lucide-react";


type ModelState =
  | "VERIFIED"
  | "PENDING";


type ModelResult = {
  state: ModelState;
  fleet_rmse_mg_l: number | null;
  farms: Record<
    string,
    {
      rmse_mg_l: number;
      horizon_hours: number;
      horizon_steps: number;
      interval_minutes: number;
      status: string;
    }
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

  farm_matrix: Record<
    string,
    Record<string, number | null>
  >;

  fleet_rmse_mg_l: Record<
    string,
    number | null
  >;

  change_vs_persistence_pct: Record<
    string,
    number | null
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


export default function ModelsPage() {

  const [data, setData] =
    useState<BenchmarkData | null>(
      null,
    );

  const [error, setError] =
    useState<string | null>(
      null,
    );


  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

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

        const result = (await response.json()) as BenchmarkData;

        if (!cancelled) {
          setData(result);
        }

      } catch {

        if (!cancelled) {
          setError(
            "Unable to load benchmark results.",
          );
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };

  }, []);


  if (error) {

    return (
      <main className="min-h-screen bg-background">
        <div className="mx-auto max-w-[1500px] px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6 text-sm text-destructive">
            {error}
          </div>
        </div>
      </main>
    );
  }


  if (!data) {

    return (
      <main className="min-h-screen bg-background">
        <div className="mx-auto max-w-[1500px] px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-border bg-card p-8 text-center">
            <p className="text-sm font-semibold">
              Loading benchmark
            </p>

            <p className="mt-2 text-xs text-muted-foreground">
              Loading verified public Task-1 results.
            </p>
          </div>
        </div>
      </main>
    );
  }


  const verifiedModels =
    MODEL_ORDER.filter(
      (modelName) =>
        data.models[modelName]?.state ===
        "VERIFIED",
    );


  const verifiedFleetValues =
    verifiedModels
      .map(
        (modelName) =>
          data.models[modelName]
            ?.fleet_rmse_mg_l,
      )
      .filter(
        (
          value,
        ): value is number =>
          typeof value ===
          "number",
      );


  const measuredCount =
    verifiedFleetValues.length;


  return (
    <main className="min-h-screen bg-background">

      <div className="mx-auto w-full max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">

        <div className="flex flex-col gap-6">

          <section className="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-8">

            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">

              <div className="max-w-3xl">

                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  <BarChart3 className="h-4 w-4" />
                  Model intelligence
                </div>

                <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
                  Model Benchmark
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
                  Measured public Task-1 results for 72-hour dissolved-oxygen
                  forecasting across farms A1, B1, and C1.
                </p>

              </div>


              <div className="grid grid-cols-2 gap-3">

                <SummaryCard
                  label="Evaluated models"
                  value={`${measuredCount}`}
                />

                <SummaryCard
                  label="Forecast horizon"
                  value="72h"
                />

              </div>

            </div>


            <div className="mt-8 flex flex-wrap gap-2">

              <StatusPill
                icon={
                  <Database className="h-3.5 w-3.5" />
                }
                text="Public A1 / B1 / C1"
              />

              <StatusPill
                icon={
                  <CheckCircle2 className="h-3.5 w-3.5" />
                }
                text="Independently computed"
              />

              <StatusPill
                icon={
                  <Clock3 className="h-3.5 w-3.5" />
                }
                text="15-minute interval"
              />

            </div>

          </section>


          <section>

            <div className="mb-4">

              <p className="text-sm font-semibold">
                Model results
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Fleet RMSE is read from the verified benchmark result artifacts.
              </p>

            </div>


            <div className="grid gap-4 xl:grid-cols-4">

              {MODEL_ORDER.map(
                (modelName) => {

                  const model =
                    data.models[
                      modelName
                    ];

                  if (!model) {
                    return null;
                  }

                  return (
                    <ModelCard
                      key={modelName}
                      name={modelName}
                      state={model.state}
                      fleetRmse={
                        model.fleet_rmse_mg_l
                      }
                    />
                  );
                },
              )}

            </div>

          </section>


          <section className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">

            <div className="border-b border-border p-5">

              <p className="text-sm font-semibold">
                Farm-level RMSE
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                DO RMSE in mg/L for the common 72-hour Task-1 protocol.
              </p>

            </div>


            <div className="overflow-x-auto">

              <table className="w-full min-w-[820px] text-sm">

                <thead>

                  <tr className="border-b border-border text-left text-xs text-muted-foreground">

                    <th className="px-5 py-4 font-medium">
                      Farm
                    </th>

                    {MODEL_ORDER.map(
                      (modelName) => (
                        <th
                          key={modelName}
                          className="px-5 py-4 font-medium"
                        >
                          {modelName}
                        </th>
                      ),
                    )}

                  </tr>

                </thead>


                <tbody>

                  {data.task.farms.map(
                    (farmId) => (
                      <tr
                        key={farmId}
                        className="border-b border-border last:border-0"
                      >

                        <td className="px-5 py-4 font-semibold">
                          {farmId}
                        </td>

                        {MODEL_ORDER.map(
                          (modelName) => {

                            const value =
                              data.farm_matrix[
                                farmId
                              ]?.[
                                modelName
                              ];

                            return (
                              <td
                                key={modelName}
                                className="px-5 py-4"
                              >
                                {value ===
                                null ||
                                value ===
                                undefined
                                  ? (
                                    <span className="text-xs text-muted-foreground">
                                      Pending
                                    </span>
                                  )
                                  : (
                                    <span className="font-medium">
                                      {value.toFixed(4)}
                                    </span>
                                  )}
                              </td>
                            );
                          },
                        )}

                      </tr>
                    ),
                  )}

                </tbody>

              </table>

            </div>

          </section>


          <section className="grid gap-4 lg:grid-cols-2">

            <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <ArrowRight className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Change vs persistence
                </p>

              </div>

              <p className="mt-1 text-xs text-muted-foreground">
                Relative fleet RMSE change calculated from the measured reports.
              </p>


              <div className="mt-5 space-y-3">

                {[
                  "XGBoost",
                  "Random Forest",
                  "LSTM",
                ].map(
                  (modelName) => {

                    const change =
                      data.change_vs_persistence_pct[
                        modelName
                      ];

                    return (
                      <div
                        key={modelName}
                        className="flex items-center justify-between rounded-xl border border-border p-3"
                      >

                        <span className="text-xs font-semibold">
                          {modelName}
                        </span>

                        <span className="text-xs text-muted-foreground">
                          {change === null ||
                          change === undefined
                            ? "Pending"
                            : `${change.toFixed(2)}%`}
                        </span>

                      </div>
                    );

                  },
                )}

              </div>

            </div>


            <div className="rounded-2xl border border-border bg-muted/20 p-5">

              <div className="flex items-center gap-2">

                <ShieldCheck className="h-4 w-4" />

                <p className="text-sm font-semibold">
                  Validation boundary
                </p>

              </div>

              <div className="mt-4 space-y-2 text-xs text-muted-foreground">

                <p>
                  Data scope: public A1 / B1 / C1 sample data.
                </p>

                <p>
                  Commercial 12-farm validation: not performed.
                </p>

                <p>
                  Real-world validation: not performed.
                </p>

                <p>
                  Automatic model ranking: disabled.
                </p>

                <p>
                  Production accuracy claim: not made.
                </p>

              </div>

            </div>

          </section>


          <section className="rounded-2xl border border-border bg-muted/20 p-5">

            <div className="flex items-start gap-3">

              <Database className="mt-0.5 h-4 w-4" />

              <div>

                <p className="text-sm font-semibold">
                  Provenance
                </p>

                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                  The browser-facing benchmark dataset is generated from the
                  existing independently computed report artifacts. The UI
                  does not treat source-reported leaderboard numbers as
                  independent measurements.
                </p>

              </div>

            </div>

          </section>

        </div>

      </div>

    </main>
  );
}


function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-muted/20 p-4">

      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold">
        {value}
      </p>

    </div>
  );
}


function StatusPill({
  icon,
  text,
}: {
  icon: React.ReactNode;
  text: string;
}) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs font-semibold">
      {icon}
      {text}
    </span>
  );
}


function ModelCard({
  name,
  state,
  fleetRmse,
}: {
  name: string;
  state: ModelState;
  fleetRmse: number | null;
}) {

  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between gap-3">

        <div>

          <p className="text-sm font-semibold">
            {name}
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Task-1 baseline
          </p>

        </div>

        <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-[10px] font-semibold">

          {state === "VERIFIED" ? (
            <CheckCircle2 className="h-3.5 w-3.5" />
          ) : (
            <Clock3 className="h-3.5 w-3.5" />
          )}

          {state === "VERIFIED"
            ? "Verified"
            : "Pending"}

        </span>

      </div>


      <div className="mt-6">

        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Fleet RMSE
        </p>

        <p className="mt-1 text-2xl font-semibold tracking-tight">

          {fleetRmse === null
            ? "—"
            : fleetRmse.toFixed(4)}

          {fleetRmse !== null && (
            <span className="ml-1 text-xs font-normal text-muted-foreground">
              mg/L
            </span>
          )}

        </p>

      </div>

    </div>
  );
}

