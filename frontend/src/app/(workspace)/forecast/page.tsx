"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  BrainCircuit,
  Droplets,
  Gauge,
  RefreshCw,
  Thermometer,
} from "lucide-react";

import {
  FarmPondSelector,
} from "@/components/app-shell/farm-pond-selector";

import {
  ForecastHeader,
} from "@/components/forecast/forecast-header";

import {
  ForecastMetricCard,
} from "@/components/forecast/forecast-metric-card";

import {
  ForecastUnavailable,
} from "@/components/forecast/forecast-unavailable";

import {
  ObservedTrend,
} from "@/components/forecast/observed-trend";

import {
  listWaterQuality,
  type WaterQualityMeasurement,
} from "@/lib/api/water-quality";

import type { Farm } from "@/lib/api/farms";
import type { Pond } from "@/lib/api/ponds";


export default function ForecastPage() {
  const [farm, setFarm] = useState<Farm | null>(null);
  const [pond, setPond] = useState<Pond | null>(null);

  const [measurements, setMeasurements] =
    useState<WaterQualityMeasurement[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] =
    useState<string | null>(null);


  async function loadMeasurements(
    pondId: string | null,
  ) {
    if (!pondId) {
      setMeasurements([]);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result =
        await listWaterQuality(pondId);

      setMeasurements(result);
    } catch {
      setMeasurements([]);
      setError(
        "Unable to load observations for the selected pond.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadMeasurements(
      pond?.id ?? null,
    );
  }, [pond?.id]);


  const latest =
    useMemo(() => {
      const result:
        Record<string, WaterQualityMeasurement> = {};

      for (const measurement of measurements) {
        const current =
          result[measurement.parameter];

        if (
          !current ||
          new Date(
            measurement.measured_at,
          ).getTime() >
            new Date(
              current.measured_at,
            ).getTime()
        ) {
          result[measurement.parameter] =
            measurement;
        }
      }

      return result;
    }, [measurements]);


  function findLatest(
    ...names: string[]
  ) {
    for (const name of names) {
      if (latest[name]) {
        return latest[name];
      }
    }

    return null;
  }


  const oxygen = findLatest(
    "DO",
    "dissolved_oxygen",
    "dissolved_oxygen_mg_l",
    "Dissolved Oxygen",
  );

  const ph = findLatest(
    "pH",
    "ph",
    "PH",
  );

  const temperature = findLatest(
    "temperature",
    "Temperature",
    "temperature_c",
  );

  const ammonia = findLatest(
    "ammonia",
    "TAN",
    "ammonia_mg_l",
  );


  return (
    <div className="w-full px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      <div className="mx-auto w-full max-w-[1500px]">

        <div className="flex flex-col gap-6">

          <ForecastHeader
            farmName={farm?.name ?? null}
            pondName={pond?.name ?? null}
          />

          <FarmPondSelector
            onFarmChange={setFarm}
            onPondChange={setPond}
          />

          {error && (
            <div className="flex items-start gap-3 rounded-2xl border border-destructive/20 bg-destructive/5 p-4">
              <AlertCircle className="mt-0.5 h-4 w-4 text-destructive" />

              <div>
                <p className="text-sm font-semibold">
                  Observation request failed
                </p>

                <p className="mt-1 text-xs text-destructive/80">
                  {error}
                </p>
              </div>
            </div>
          )}

          <section>
            <div className="mb-4 flex items-end justify-between gap-4">

              <div>
                <p className="text-sm font-semibold">
                  Current observations
                </p>

                <p className="mt-1 text-xs text-muted-foreground">
                  Latest recorded measurements for the selected pond.
                </p>
              </div>

              <button
                type="button"
                disabled={
                  loading ||
                  !pond
                }
                onClick={() =>
                  void loadMeasurements(
                    pond?.id ?? null,
                  )
                }
                className="inline-flex items-center gap-2 rounded-xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCw
                  className={
                    loading
                      ? "h-3.5 w-3.5 animate-spin"
                      : "h-3.5 w-3.5"
                  }
                />
                Refresh
              </button>

            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <ForecastMetricCard
                label="Dissolved oxygen"
                value={oxygen?.value ?? null}
                unit={oxygen?.unit ?? "mg/L"}
                timestamp={
                  oxygen?.measured_at ?? null
                }
              />

              <ForecastMetricCard
                label="pH"
                value={ph?.value ?? null}
                unit={ph?.unit ?? "pH"}
                timestamp={ph?.measured_at ?? null}
              />

              <ForecastMetricCard
                label="Temperature"
                value={temperature?.value ?? null}
                unit={temperature?.unit ?? "°C"}
                timestamp={
                  temperature?.measured_at ?? null
                }
              />

              <ForecastMetricCard
                label="Ammonia / TAN"
                value={ammonia?.value ?? null}
                unit={ammonia?.unit ?? "mg/L"}
                timestamp={
                  ammonia?.measured_at ?? null
                }
              />

            </div>
          </section>

          <ObservedTrend
            measurements={measurements}
          />

          <ForecastUnavailable />

          <section className="grid gap-4 md:grid-cols-3">

            <InfoCard
              title="Forecast horizon"
              value="72 hours"
              icon={
                <Gauge className="h-4 w-4" />
              }
            />

            <InfoCard
              title="Forecast status"
              value="Not connected"
              icon={
                <Activity className="h-4 w-4" />
              }
            />

            <InfoCard
              title="Model metadata"
              value="Awaiting model service"
              icon={
                <BrainCircuit className="h-4 w-4" />
              }
            />

          </section>

        </div>
      </div>
    </div>
  );
}


function InfoCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}

        <p className="text-[10px] font-semibold uppercase tracking-[0.16em]">
          {title}
        </p>
      </div>

      <p className="mt-3 text-sm font-semibold">
        {value}
      </p>

    </div>
  );
}
