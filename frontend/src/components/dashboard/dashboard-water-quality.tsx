"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  Droplets,
  Gauge,
  RefreshCw,
  Thermometer,
} from "lucide-react";

import {
  listWaterQuality,
  type WaterQualityMeasurement,
} from "@/lib/api/water-quality";


type Props = {
  pondId: string | null;
};


export function DashboardWaterQuality({
  pondId,
}: Props) {

  const [measurements, setMeasurements] =
    useState<WaterQualityMeasurement[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function load() {

    if (!pondId) {
      setMeasurements([]);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {

      const result =
        await listWaterQuality(
          pondId,
        );

      setMeasurements(result);

    } catch {

      setMeasurements([]);

      setError(
        "Unable to load pond observations.",
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    void load();

  }, [pondId]);


  const latest =
    useMemo(() => {

      const output:
        Record<
          string,
          WaterQualityMeasurement
        > = {};

      for (
        const item
        of measurements
      ) {

        const current =
          output[item.parameter];

        if (
          !current ||
          new Date(
            item.measured_at,
          ).getTime()
          >
          new Date(
            current.measured_at,
          ).getTime()
        ) {

          output[item.parameter] = item;

        }
      }

      return output;

    }, [measurements]);


  const find =
    (
      names: string[],
    ) => {

      for (
        const name
        of names
      ) {

        if (latest[name]) {
          return latest[name];
        }

      }

      return null;
    };


  const oxygen =
    find([
      "DO",
      "dissolved_oxygen",
      "dissolved_oxygen_mg_l",
      "Dissolved Oxygen",
    ]);

  const ph =
    find([
      "pH",
      "ph",
      "PH",
    ]);

  const temperature =
    find([
      "temperature",
      "Temperature",
      "temperature_c",
    ]);

  const tan =
    find([
      "TAN",
      "ammonia",
      "ammonia_mg_l",
    ]);


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between gap-4">

        <div>

          <p className="text-sm font-semibold">
            Water quality
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Latest recorded observations
          </p>

        </div>

        <button
          type="button"
          onClick={() => void load()}
          disabled={
            loading ||
            !pondId
          }
          className="rounded-lg border border-border p-2 text-muted-foreground transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw
            className={
              loading
                ? "h-3.5 w-3.5 animate-spin"
                : "h-3.5 w-3.5"
            }
          />
        </button>

      </div>


      {!pondId && (
        <div className="mt-5 rounded-xl border border-dashed border-border p-5 text-center">

          <p className="text-xs font-semibold">
            Select a pond
          </p>

          <p className="mt-1 text-[11px] text-muted-foreground">
            Water-quality observations will appear here.
          </p>

        </div>
      )}


      {pondId && error && (
        <div className="mt-5 rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-xs text-destructive">
          {error}
        </div>
      )}


      {pondId && !error && (
        <div className="mt-5 grid grid-cols-2 gap-3">

          <MiniMetric
            label="DO"
            value={oxygen}
            fallbackUnit="mg/L"
            icon={
              <Droplets className="h-4 w-4" />
            }
          />

          <MiniMetric
            label="pH"
            value={ph}
            fallbackUnit="pH"
            icon={
              <Gauge className="h-4 w-4" />
            }
          />

          <MiniMetric
            label="Temperature"
            value={temperature}
            fallbackUnit="°C"
            icon={
              <Thermometer className="h-4 w-4" />
            }
          />

          <MiniMetric
            label="TAN"
            value={tan}
            fallbackUnit="mg/L"
            icon={
              <Activity className="h-4 w-4" />
            }
          />

        </div>
      )}

    </section>
  );
}


function MiniMetric({
  label,
  value,
  fallbackUnit,
  icon,
}: {
  label: string;
  value: WaterQualityMeasurement | null;
  fallbackUnit: string;
  icon: React.ReactNode;
}) {

  return (
    <div className="rounded-xl border border-border bg-muted/20 p-3">

      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}

        <p className="text-[10px] font-semibold uppercase tracking-[0.14em]">
          {label}
        </p>
      </div>

      <p className="mt-3 text-lg font-semibold">
        {value
          ? format(value.value)
          : "—"}

        <span className="ml-1 text-[10px] font-normal text-muted-foreground">
          {value?.unit ?? fallbackUnit}
        </span>
      </p>

      <p className="mt-1 text-[9px] text-muted-foreground">
        {value
          ? "Observed"
          : "No observation"}
      </p>

    </div>
  );
}


function format(
  value: number,
) {

  return Number.isInteger(value)
    ? String(value)
    : value.toFixed(2);
}