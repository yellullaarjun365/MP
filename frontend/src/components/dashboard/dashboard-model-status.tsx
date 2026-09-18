"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  BrainCircuit,
  CheckCircle2,
  Clock3,
} from "lucide-react";


type ModelState =
  | "VERIFIED"
  | "PENDING";


type Model = {
  state: ModelState;

  fleet_rmse_mg_l:
    number | null;
};


type BenchmarkData = {
  models: Record<
    string,
    Model
  >;
};


const MODEL_ORDER = [
  "XGBoost",
  "Random Forest",
  "LSTM",
];


export function DashboardModelStatus() {

  const [data, setData] =
    useState<BenchmarkData | null>(
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
          return;
        }

        const result = (await response.json()) as BenchmarkData;

        if (!cancelled) {
          setData(result);
        }

      } catch {
        // Dashboard model status is optional.
      }

    }

    void load();

    return () => {
      cancelled = true;
    };

  }, []);


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-semibold">
            Model status
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Task-1 benchmark state
          </p>

        </div>

        <BrainCircuit className="h-5 w-5 text-muted-foreground" />

      </div>


      <div className="mt-5 space-y-3">

        {MODEL_ORDER.map(
          (modelName) => {

            const model =
              data?.models[
                modelName
              ];

            const verified =
              model?.state ===
              "VERIFIED";

            return (
              <div
                key={modelName}
                className="flex items-center justify-between rounded-xl border border-border bg-muted/20 p-3"
              >

                <div>

                  <p className="text-xs font-semibold">
                    {modelName}
                  </p>

                  <p className="mt-1 text-[10px] text-muted-foreground">

                    {verified &&
                    model?.fleet_rmse_mg_l !== null
                      ? `Fleet RMSE ${model.fleet_rmse_mg_l.toFixed(4)} mg/L`
                      : "Benchmark result pending"}

                  </p>

                </div>


                <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold">

                  {verified ? (
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  ) : (
                    <Clock3 className="h-3.5 w-3.5" />
                  )}

                  {verified
                    ? "Verified"
                    : "Pending"}

                </span>

              </div>
            );

          },
        )}

      </div>

    </section>
  );
}