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
  Thermometer,
} from "lucide-react";

import {
  FarmPondSelector,
  FarmPondSummary,
} from "@/components/app-shell/farm-pond-selector";

import {
  WaterQualityMetricCard,
} from "@/components/dashboard/water-quality-metric-card";

import {
  WaterQualityHistory,
} from "@/components/dashboard/water-quality-history";

import {
  listWaterQuality,
  type WaterQualityMeasurement,
} from "@/lib/api/water-quality";

import type {
  Farm,
} from "@/lib/api/farms";

import type {
  Pond,
} from "@/lib/api/ponds";


export default function WaterQualityPage() {

  const [farm, setFarm] =
    useState<Farm | null>(
      null,
    );

  const [pond, setPond] =
    useState<Pond | null>(
      null,
    );

  const [measurements, setMeasurements] =
    useState<WaterQualityMeasurement[]>(
      [],
    );


  useEffect(() => {

    let cancelled = false;

    async function load() {

      if (!pond) {

        setMeasurements([]);

        return;
      }

      try {

        const result =
          await listWaterQuality(
            pond.id,
          );

        if (!cancelled) {

          setMeasurements(
            result,
          );
        }

      } catch {

        if (!cancelled) {

          setMeasurements(
            [],
          );
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };

  }, [pond]);


  const latest =
    useMemo(() => {

      const result:
        Record<
          string,
          WaterQualityMeasurement
        > = {};

      for (
        const measurement
        of measurements
      ) {

        const current =
          result[
            measurement.parameter
          ];

        if (
          !current ||
          new Date(
            measurement.measured_at,
          ).getTime()
          >
          new Date(
            current.measured_at,
          ).getTime()
        ) {

          result[
            measurement.parameter
          ] = measurement;
        }
      }

      return result;

    }, [measurements]);


  const findLatest = (
    ...names: string[]
  ) => {

    for (
      const name
      of names
    ) {

      const exact =
        latest[name];

      if (exact) {
        return exact;
      }
    }

    return null;
  };


  const oxygen =
    findLatest(
      "DO",
      "dissolved_oxygen",
      "dissolved_oxygen_mg_l",
      "Dissolved Oxygen",
    );


  const ph =
    findLatest(
      "pH",
      "ph",
      "PH",
    );


  const temperature =
    findLatest(
      "temperature",
      "Temperature",
      "temperature_c",
    );


  const ammonia =
    findLatest(
      "ammonia",
      "TAN",
      "ammonia_mg_l",
    );


  return (
    <div className="w-full">

      <div className="mx-auto w-full max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">

        <div className="flex flex-col gap-6">

          <section>

            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Operations / water quality
            </p>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
              Water Quality
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
              Monitor recorded pond measurements, inspect recent observations,
              and prepare the selected pond for future forecasting.
            </p>

          </section>


          <FarmPondSelector
            onFarmChange={setFarm}
            onPondChange={setPond}
          />


          <FarmPondSummary
            farm={farm}
            pond={pond}
          />


          <section>

            <div className="mb-4">

              <p className="text-sm font-semibold">
                Latest observations
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Most recent recorded value for each supported parameter.
              </p>

            </div>


            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <WaterQualityMetricCard
                label="Dissolved oxygen"
                value={
                  oxygen?.value ??
                  null
                }
                unit={
                  oxygen?.unit ??
                  "mg/L"
                }
                measuredAt={
                  oxygen?.measured_at ??
                  null
                }
                icon={
                  <Droplets className="h-5 w-5" />
                }
              />


              <WaterQualityMetricCard
                label="pH"
                value={
                  ph?.value ??
                  null
                }
                unit={
                  ph?.unit ??
                  "pH"
                }
                measuredAt={
                  ph?.measured_at ??
                  null
                }
                icon={
                  <Gauge className="h-5 w-5" />
                }
              />


              <WaterQualityMetricCard
                label="Temperature"
                value={
                  temperature?.value ??
                  null
                }
                unit={
                  temperature?.unit ??
                  "°C"
                }
                measuredAt={
                  temperature?.measured_at ??
                  null
                }
                icon={
                  <Thermometer className="h-5 w-5" />
                }
              />


              <WaterQualityMetricCard
                label="Ammonia / TAN"
                value={
                  ammonia?.value ??
                  null
                }
                unit={
                  ammonia?.unit ??
                  "mg/L"
                }
                measuredAt={
                  ammonia?.measured_at ??
                  null
                }
                icon={
                  <Activity className="h-5 w-5" />
                }
              />

            </div>

          </section>


          <WaterQualityHistory
            pondId={
              pond?.id ??
              null
            }
          />


          <section className="rounded-2xl border border-border bg-muted/20 p-5">

            <p className="text-sm font-semibold">
              Forecast connection
            </p>

            <p className="mt-2 max-w-3xl text-xs leading-5 text-muted-foreground">
              The measurement history now uses the real pond water-quality
              endpoint. The 72-hour forecasting workspace will consume the
              selected pond context separately once the forecasting API is
              connected.
            </p>

          </section>

        </div>

      </div>

    </div>
  );
}
