"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  Activity,
} from "lucide-react";

import type {
  WaterQualityMeasurement,
} from "@/lib/api/water-quality";

type Props = {
  measurements: WaterQualityMeasurement[];
};

export function ObservedTrend({
  measurements,
}: Props) {

  const parameters = useMemo(
    () =>
      [
        ...new Set(
          measurements.map(
            (measurement) =>
              measurement.parameter,
          ),
        ),
      ],
    [measurements],
  );

  const [
    selectedParameter,
    setSelectedParameter,
  ] = useState(
    parameters[0] ?? "",
  );

  const points =
    useMemo(
      () =>
        measurements
          .filter(
            (measurement) =>
              measurement.parameter ===
              selectedParameter,
          )
          .sort(
            (a, b) =>
              new Date(
                a.measured_at,
              ).getTime()
              -
              new Date(
                b.measured_at,
              ).getTime(),
          )
          .slice(-24),
      [
        measurements,
        selectedParameter,
      ],
    );


  if (measurements.length === 0) {

    return (
      <section className="rounded-2xl border border-border bg-card shadow-sm">

        <div className="border-b border-border p-5">

          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4" />

            <p className="text-sm font-semibold">
              Observed trend
            </p>
          </div>

        </div>

        <div className="p-8 text-center">

          <p className="text-sm font-semibold">
            No observations available
          </p>

          <p className="mt-2 text-xs text-muted-foreground">
            Recorded measurements for this pond will appear here.
          </p>

        </div>

      </section>
    );
  }


  return (
    <section className="rounded-2xl border border-border bg-card shadow-sm">

      <div className="flex flex-col gap-4 border-b border-border p-5 sm:flex-row sm:items-center sm:justify-between">

        <div>

          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4" />

            <p className="text-sm font-semibold">
              Observed trend
            </p>
          </div>

          <p className="mt-1 text-xs text-muted-foreground">
            Recent recorded observations only
          </p>

        </div>

        <div className="flex flex-wrap gap-2">

          {parameters.map(
            (parameter) => (
              <button
                key={parameter}
                type="button"
                onClick={() =>
                  setSelectedParameter(
                    parameter,
                  )
                }
                className={[
                  "rounded-xl border px-3 py-2 text-xs font-semibold transition",
                  selectedParameter ===
                    parameter
                    ? "border-foreground bg-foreground text-background"
                    : "border-border hover:bg-muted",
                ].join(" ")}
              >
                {parameter}
              </button>
            ),
          )}

        </div>

      </div>

      <div className="p-5">

        <div className="overflow-x-auto">

          <div className="grid min-w-[640px] grid-cols-6 gap-3">

            {points.map(
              (point) => (
                <div
                  key={point.id}
                  className="rounded-xl border border-border bg-muted/20 p-3"
                >

                  <p className="text-[10px] text-muted-foreground">
                    {formatShortDate(
                      point.measured_at,
                    )}
                  </p>

                  <p className="mt-2 text-sm font-semibold">
                    {formatValue(
                      point.value,
                    )}
                  </p>

                  <p className="mt-1 text-[10px] text-muted-foreground">
                    {point.unit}
                  </p>

                </div>
              ),
            )}

          </div>

        </div>

      </div>

    </section>
  );
}


function formatValue(
  value: number,
) {
  return Number.isInteger(value)
    ? String(value)
    : value.toFixed(2);
}


function formatShortDate(
  value: string,
) {

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    undefined,
    {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    },
  );
}
