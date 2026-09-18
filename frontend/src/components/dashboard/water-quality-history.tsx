"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  Clock3,
  RefreshCw,
} from "lucide-react";

import {
  listWaterQuality,
  type WaterQualityMeasurement,
} from "@/lib/api/water-quality";


type Props = {
  pondId: string | null;
};


export function WaterQualityHistory({
  pondId,
}: Props) {

  const [measurements, setMeasurements] =
    useState<WaterQualityMeasurement[]>(
      [],
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null,
    );

  const [
    selectedParameter,
    setSelectedParameter,
  ] = useState<string>("");


  async function loadMeasurements() {

    if (!pondId) {

      setMeasurements([]);

      setSelectedParameter("");

      return;
    }

    setLoading(true);

    setError(null);

    try {

      const result =
        await listWaterQuality(
          pondId,
        );

      const sorted =
        [...result].sort(
          (a, b) =>
            new Date(
              a.measured_at,
            ).getTime()
            -
            new Date(
              b.measured_at,
            ).getTime(),
        );

      setMeasurements(
        sorted,
      );

      const parameters = [
        ...new Set(
          sorted.map(
            (item) =>
              item.parameter,
          ),
        ),
      ];

      setSelectedParameter(
        (current) =>
          current &&
          parameters.includes(
            current,
          )
            ? current
            : parameters[0] ?? "",
      );

    } catch {

      setMeasurements([]);

      setError(
        "Unable to load water-quality measurements.",
      );

    } finally {

      setLoading(false);
    }
  }


  useEffect(() => {

    void loadMeasurements();

  }, [pondId]);


  const parameters =
    useMemo(
      () =>
        [
          ...new Set(
            measurements.map(
              (item) =>
                item.parameter,
            ),
          ),
        ],
      [measurements],
    );


  const selectedMeasurements =
    measurements.filter(
      (item) =>
        item.parameter ===
        selectedParameter,
    );


  return (
    <section className="rounded-2xl border border-border bg-card shadow-sm">

      <div className="flex flex-col gap-4 border-b border-border p-5 sm:flex-row sm:items-center sm:justify-between">

        <div>

          <div className="flex items-center gap-2">

            <Activity className="h-4 w-4" />

            <p className="text-sm font-semibold">
              Measurement history
            </p>

          </div>

          <p className="mt-1 text-xs text-muted-foreground">
            Recorded water-quality observations for the selected pond.
          </p>

        </div>

        <button
          type="button"
          onClick={() => void loadMeasurements()}
          disabled={
            loading ||
            !pondId
          }
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RefreshCw
            className={[
              "h-3.5 w-3.5",
              loading
                ? "animate-spin"
                : "",
            ].join(" ")}
          />
          Refresh
        </button>

      </div>


      <div className="p-5">

        {!pondId && (
          <EmptyState
            title="Select a pond"
            text="Choose a pond above to view its measurements."
          />
        )}


        {pondId &&
          loading &&
          measurements.length === 0 && (
            <EmptyState
              title="Loading measurements"
              text="Fetching recorded water-quality observations."
            />
          )}


        {pondId &&
          !loading &&
          error && (
            <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-xs text-destructive">
              {error}
            </div>
          )}


        {pondId &&
          !loading &&
          !error &&
          measurements.length === 0 && (
            <EmptyState
              title="No measurements yet"
              text="This pond does not currently have recorded water-quality observations."
            />
          )}


        {parameters.length > 0 && (
          <>

            <div className="mb-5 flex flex-wrap gap-2">

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


            {selectedMeasurements.length > 0 && (
              <div className="overflow-x-auto">

                <table className="w-full min-w-[640px] text-sm">

                  <thead>

                    <tr className="border-b border-border text-left text-xs text-muted-foreground">

                      <th className="px-3 py-3 font-medium">
                        Time
                      </th>

                      <th className="px-3 py-3 font-medium">
                        Parameter
                      </th>

                      <th className="px-3 py-3 font-medium">
                        Value
                      </th>

                      <th className="px-3 py-3 font-medium">
                        Source
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {[...selectedMeasurements]
                      .reverse()
                      .slice(0, 50)
                      .map(
                        (measurement) => (
                          <tr
                            key={measurement.id}
                            className="border-b border-border last:border-0"
                          >

                            <td className="px-3 py-3 text-xs text-muted-foreground">
                              <span className="inline-flex items-center gap-1.5">
                                <Clock3 className="h-3.5 w-3.5" />
                                {formatDate(
                                  measurement.measured_at,
                                )}
                              </span>
                            </td>

                            <td className="px-3 py-3 text-xs font-medium">
                              {measurement.parameter}
                            </td>

                            <td className="px-3 py-3 text-sm font-semibold">
                              {measurement.value}{" "}
                              <span className="text-xs font-normal text-muted-foreground">
                                {measurement.unit}
                              </span>
                            </td>

                            <td className="px-3 py-3 text-xs text-muted-foreground">
                              {measurement.source}
                            </td>

                          </tr>
                        ),
                      )}

                  </tbody>

                </table>

              </div>
            )}

          </>
        )}

      </div>

    </section>
  );
}


function EmptyState({
  title,
  text,
}: {
  title: string;
  text: string;
}) {

  return (
    <div className="rounded-2xl border border-dashed border-border p-8 text-center">

      <p className="text-sm font-semibold">
        {title}
      </p>

      <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-muted-foreground">
        {text}
      </p>

    </div>
  );
}


function formatDate(
  value: string,
) {

  const date =
    new Date(value);

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
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}
