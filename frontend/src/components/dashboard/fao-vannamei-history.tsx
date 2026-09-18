"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getIndiaVannameiHistory,
  type FaoVannameiHistory,
} from "@/lib/api/fao";


function numberFormat(
  value: number,
  digits = 0,
): string {
  return new Intl.NumberFormat(
    "en-IN",
    {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits,
    },
  ).format(value);
}


function tonnesLabel(
  value: number,
): string {

  if (value >= 1_000_000) {
    return `${numberFormat(
      value / 1_000_000,
      2,
    )}M t`;
  }

  if (value >= 1_000) {
    return `${numberFormat(
      value / 1_000,
      1,
    )}k t`;
  }

  return `${numberFormat(
    value,
    0,
  )} t`;
}


export function FaoVannameiHistory() {

  const [
    data,
    setData,
  ] = useState<FaoVannameiHistory | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );


  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

        const result =
          await getIndiaVannameiHistory();

        if (!cancelled) {
          setData(result);
        }

      } catch (cause) {

        if (!cancelled) {

          setError(
            cause instanceof Error
              ? cause.message
              : "Unable to load FAO history.",
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


  const maxProduction =
    useMemo(() => {

      if (
        !data ||
        data.yearly_production.length === 0
      ) {
        return 1;
      }

      return Math.max(
        ...data.yearly_production.map(
          (row) => row.production_tonnes,
        ),
      );

    }, [data]);


  if (loading) {

    return (
      <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

        <div className="animate-pulse space-y-4">

          <div className="h-5 w-64 rounded bg-muted" />

          <div className="h-4 w-96 max-w-full rounded bg-muted" />

          <div className="h-56 rounded-xl bg-muted" />

        </div>

      </section>
    );
  }


  if (error) {

    return (
      <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

        <div className="space-y-2">

          <div className="text-sm font-semibold">
            India Vannamei Production History
          </div>

          <div className="text-sm text-destructive">
            {error}
          </div>

        </div>

      </section>
    );
  }


  if (!data) {
    return null;
  }


  const latest =
    data.yearly_production[
      data.yearly_production.length - 1
    ];


  const latestEnvironment =
    data.environment_breakdown.filter(
      (row) =>
        row.year === data.last_year,
    );


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

        <div>

          <div className="text-sm font-semibold">
            India Vannamei Production History
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            FAO Global Aquaculture Production ·
            Release {data.release}
          </div>

        </div>

        <div className="flex flex-wrap gap-2">

          <span className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
            Real-world statistics
          </span>

          <span className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
            Through {data.data_through}
          </span>

        </div>

      </div>


      <div className="mt-5 grid gap-3 md:grid-cols-4">

        <div className="rounded-xl border border-border p-4">

          <div className="text-xs text-muted-foreground">
            Latest production
          </div>

          <div className="mt-1 text-2xl font-semibold">
            {tonnesLabel(
              latest.production_tonnes,
            )}
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            {latest.year}
          </div>

        </div>


        <div className="rounded-xl border border-border p-4">

          <div className="text-xs text-muted-foreground">
            YoY change
          </div>

          <div className="mt-1 text-2xl font-semibold">

            {latest.yoy_change_pct === null
              ? "—"
              : `${latest.yoy_change_pct >= 0 ? "+" : ""}${numberFormat(
                  latest.yoy_change_pct,
                  1,
                )}%`}

          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            previous observed year
          </div>

        </div>


        <div className="rounded-xl border border-border p-4">

          <div className="text-xs text-muted-foreground">
            Observed years
          </div>

          <div className="mt-1 text-2xl font-semibold">
            {data.year_count}
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            {data.first_year}–{data.last_year}
          </div>

        </div>


        <div className="rounded-xl border border-border p-4">

          <div className="text-xs text-muted-foreground">
            Observation status
          </div>

          <div className="mt-1 text-2xl font-semibold">
            {data.official_observations}
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            official · {data.imputed_observations} imputed
          </div>

        </div>

      </div>


      <div className="mt-6">

        <div className="mb-3 flex items-end justify-between">

          <div>

            <div className="text-sm font-medium">
              Annual production
            </div>

            <div className="text-xs text-muted-foreground">
              Tonnes
            </div>

          </div>

          <div className="text-xs text-muted-foreground">
            {data.first_year} → {data.last_year}
          </div>

        </div>


        <div className="overflow-x-auto">

          <div
            className="flex min-w-[760px] items-end gap-2"
            style={{
              height: 280,
            }}
          >

            {data.yearly_production.map(
              (row) => {

                const height = Math.max(
                  8,
                  Math.round(
                    (
                      row.production_tonnes
                      /
                      maxProduction
                    )
                    *
                    220,
                  ),
                );


                return (
                  <div
                    key={row.year}
                    className="flex h-full min-w-[36px] flex-1 flex-col justify-end"
                    title={`${row.year}: ${numberFormat(
                      row.production_tonnes,
                      0,
                    )} tonnes`}
                  >

                    <div className="flex h-full items-end justify-center">

                      <div
                        className="w-full max-w-10 rounded-t-md bg-primary/80 transition hover:bg-primary"
                        style={{
                          height: `${height}px`,
                        }}
                      />

                    </div>

                    <div className="mt-2 text-center text-[10px] text-muted-foreground">
                      {row.year}
                    </div>

                  </div>
                );
              },
            )}

          </div>

        </div>

      </div>


      {data.missing_years.length > 0 && (

        <div className="mt-4 rounded-xl border border-border bg-muted/30 p-3">

          <div className="text-xs font-medium">
            Missing observations
          </div>

          <div className="mt-1 text-xs text-muted-foreground">
            No FAO observation is present for{" "}
            {data.missing_years.join(", ")}.
            Missing years are not interpolated.
          </div>

        </div>

      )}


      <div className="mt-4 grid gap-3 md:grid-cols-2">

        <div className="rounded-xl border border-border p-4">

          <div className="text-xs font-medium">
            {data.last_year} environment breakdown
          </div>

          <div className="mt-3 space-y-3">

            {latestEnvironment.map(
              (row) => (

                <div
                  key={`${row.year}-${row.environment_code}`}
                  className="flex items-center justify-between gap-4"
                >

                  <div>

                    <div className="text-sm">
                      {row.environment}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {row.environment_code} ·
                      status {row.status ?? "—"}
                    </div>

                  </div>

                  <div className="text-sm font-medium">
                    {numberFormat(
                      row.production_tonnes,
                      0,
                    )} t
                  </div>

                </div>

              ),
            )}

          </div>

        </div>


        <div className="rounded-xl border border-border p-4">

          <div className="text-xs font-medium">
            Data boundary
          </div>

          <div className="mt-3 space-y-2 text-xs text-muted-foreground">

            <div>
              Provider:{" "}
              <span className="text-foreground">
                {data.source_information.provider ?? "—"}
              </span>
            </div>

            <div>
              Coverage:{" "}
              <span className="text-foreground">
                {data.source_information.coverage ?? "—"}
              </span>
            </div>

            <div>
              This is aggregated historical FAO
              statistics, not pond-level prediction input.
            </div>

            <div>
              Model training:{" "}
              <span className="text-foreground">
                No
              </span>
            </div>

          </div>

        </div>

      </div>


      <div className="mt-4 text-xs text-muted-foreground">
        Source: FAO · Release {data.release} ·
        Data through {data.data_through}
      </div>

    </section>
  );
}
