"use client";

import { useEffect, useState } from "react";
import {
  BrainCircuit,
  Calculator,
  Loader2,
  TrendingUp,
} from "lucide-react";

import {
  predictProduction,
  type ProductionPredictionOutput,
} from "@/lib/api/prediction";
import {
  listFarms,
  type Farm,
} from "@/lib/api/farms";

import {
  listFarmPonds,
  type Pond,
} from "@/lib/api/ponds";


type FormState = {
  pond_area_m2: string;
  pond_depth_m: string;
  stocking_count: string;
  initial_average_weight_g: string;
  culture_days: string;
  survival_rate: string;
  growth_rate_g_week: string;
};


const INITIAL_FORM: FormState = {
  pond_area_m2: "1000",
  pond_depth_m: "1.5",
  stocking_count: "50000",
  initial_average_weight_g: "1",
  culture_days: "120",
  survival_rate: "0.85",
  growth_rate_g_week: "1.35",
};


function toNumber(
  value: string,
): number | null {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return null;
  }

  return parsed;
}


export function ProductionPredictionCard() {
  const [form, setForm] =
    useState<FormState>(
      INITIAL_FORM,
    );

  const [result, setResult] =
    useState<ProductionPredictionOutput | null>(
      null,
    );

  const [error, setError] =
    useState<string | null>(
      null,
    );

  const [loading, setLoading] =
    useState(false);

  const [farms, setFarms] =
    useState<Farm[]>([]);

  const [ponds, setPonds] =
    useState<Pond[]>([]);

  const [selectedFarmId, setSelectedFarmId] =
    useState("");

  const [selectedPondId, setSelectedPondId] =
    useState("");

  const [loadingFarms, setLoadingFarms] =
    useState(false);

  const [loadingPonds, setLoadingPonds] =
    useState(false);

  const [dataError, setDataError] =
    useState<string | null>(null);


  useEffect(() => {
    let cancelled = false;

    async function loadFarms() {
      setLoadingFarms(true);
      setDataError(null);

      try {
        const result = await listFarms();

        if (cancelled) {
          return;
        }

        setFarms(result);

        if (result.length > 0) {
          setSelectedFarmId(result[0].id);
        }
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setDataError(
          requestError instanceof Error
            ? requestError.message
            : "Could not load farms.",
        );
      } finally {
        if (!cancelled) {
          setLoadingFarms(false);
        }
      }
    }

    loadFarms();

    return () => {
      cancelled = true;
    };
  }, []);


  useEffect(() => {
    if (!selectedFarmId) {
      setPonds([]);
      setSelectedPondId("");
      return;
    }

    let cancelled = false;

    async function loadPonds() {
      setLoadingPonds(true);
      setDataError(null);

      try {
        const result =
          await listFarmPonds(
            selectedFarmId,
          );

        if (cancelled) {
          return;
        }

        const nextPonds =
          Array.isArray(result.value)
            ? result.value
            : [];

        setPonds(nextPonds);

        if (nextPonds.length > 0) {
          setSelectedPondId(
            nextPonds[0].id,
          );
        } else {
          setSelectedPondId("");
        }
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setDataError(
          requestError instanceof Error
            ? requestError.message
            : "Could not load ponds.",
        );
      } finally {
        if (!cancelled) {
          setLoadingPonds(false);
        }
      }
    }

    loadPonds();

    return () => {
      cancelled = true;
    };
  }, [selectedFarmId]);


  useEffect(() => {
    if (!selectedPondId) {
      return;
    }

    const pond =
      ponds.find(
        (item) =>
          item.id === selectedPondId,
      );

    if (!pond) {
      return;
    }

    setForm((current) => ({
      ...current,

      pond_area_m2:
        pond.area_m2 !== null
          ? String(
              pond.area_m2,
            )
          : current.pond_area_m2,

      pond_depth_m:
        pond.depth_m !== null
          ? String(
              pond.depth_m,
            )
          : current.pond_depth_m,
    }));
  }, [
    selectedPondId,
    ponds,
  ]);


  function updateField(
    field: keyof FormState,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  async function handlePredict() {
    setError(null);
    setResult(null);

    const pondArea =
      toNumber(
        form.pond_area_m2,
      );

    const pondDepth =
      toNumber(
        form.pond_depth_m,
      );

    const stockingCount =
      toNumber(
        form.stocking_count,
      );

    const initialWeight =
      toNumber(
        form.initial_average_weight_g,
      );

    const cultureDays =
      toNumber(
        form.culture_days,
      );

    const survivalRate =
      toNumber(
        form.survival_rate,
      );

    const growthRate =
      toNumber(
        form.growth_rate_g_week,
      );


    const invalid =
      pondArea === null ||
      pondDepth === null ||
      stockingCount === null ||
      initialWeight === null ||
      cultureDays === null ||
      survivalRate === null ||
      growthRate === null;


    if (invalid) {
      setError(
        "Enter valid numeric values in every prediction field.",
      );
      return;
    }


    if (pondArea <= 0) {
      setError(
        "Pond area must be greater than 0.",
      );
      return;
    }


    if (pondDepth <= 0) {
      setError(
        "Pond depth must be greater than 0.",
      );
      return;
    }


    if (stockingCount <= 0) {
      setError(
        "Stocking count must be greater than 0.",
      );
      return;
    }


    if (initialWeight <= 0) {
      setError(
        "Initial average weight must be greater than 0.",
      );
      return;
    }


    if (cultureDays <= 0) {
      setError(
        "Culture duration must be greater than 0.",
      );
      return;
    }


    if (
      survivalRate <= 0 ||
      survivalRate > 1
    ) {
      setError(
        "Survival rate must be between 0 and 1.",
      );
      return;
    }


    if (
      growthRate <= 0 ||
      growthRate > 3
    ) {
      setError(
        "Growth rate must be between 0 and 3 g/week.",
      );
      return;
    }


    setLoading(true);

    try {

      const prediction =
        await predictProduction({
          species:
            ponds.find(
              (pond) =>
                pond.id === selectedPondId,
            )?.species?.scientific_name
            ??
            "Litopenaeus vannamei",

          pond_area_m2:
            pondArea,

          pond_depth_m:
            pondDepth,

          stocking_count:
            stockingCount,

          initial_average_weight_g:
            initialWeight,

          culture_days:
            cultureDays,

          survival_rate:
            survivalRate,

          growth_rate_g_week:
            growthRate,
        });


      setResult(
        prediction,
      );

    } catch (requestError) {

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Prediction request failed.",
      );

    } finally {

      setLoading(false);
    }
  }


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

        <div className="flex items-start gap-3">

          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-muted">

            <BrainCircuit className="h-5 w-5" />

          </div>

          <div>

            <p className="text-sm font-semibold">
              Production prediction
            </p>

            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              Estimate expected production from your current
              pond and culture assumptions.
            </p>

          </div>

        </div>

        <span className="inline-flex w-fit items-center gap-1 rounded-full border border-border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wider text-muted-foreground">
          CatBoost V0.2
        </span>

      </div>


      <div className="mt-6 grid gap-4 sm:grid-cols-2">

        <PredictionSelect
          label="Farm"
          value={selectedFarmId}
          disabled={loadingFarms}
          placeholder={
            loadingFarms
              ? "Loading farms..."
              : farms.length === 0
                ? "No farms available"
                : "Select farm"
          }
          options={farms.map((farm) => ({
            value: farm.id,
            label: farm.name,
          }))}
          onChange={setSelectedFarmId}
        />

        <PredictionSelect
          label="Pond"
          value={selectedPondId}
          disabled={
            loadingPonds ||
            !selectedFarmId
          }
          placeholder={
            loadingPonds
              ? "Loading ponds..."
              : ponds.length === 0
                ? "No ponds available"
                : "Select pond"
          }
          options={ponds.map((pond) => ({
            value: pond.id,
            label:
              pond.species?.common_name
                ? `${pond.name} · ${pond.species.common_name}`
                : pond.name,
          }))}
          onChange={setSelectedPondId}
        />

      </div>

      {selectedPondId && (
        <div className="mt-4 rounded-xl border border-border bg-muted/20 px-4 py-3">
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-[10px] text-muted-foreground">

            <span>
              Pond data loaded from AquaLife
            </span>

            {(() => {
              const pond =
                ponds.find(
                  (item) =>
                    item.id === selectedPondId,
                );

              if (!pond) {
                return null;
              }

              return (
                <>
                  <span>
                    Area:{" "}
                    <strong className="text-foreground">
                      {pond.area_m2 === null
                        ? "Not recorded"
                        : `${pond.area_m2} m²`}
                    </strong>
                  </span>

                  <span>
                    Depth:{" "}
                    <strong className="text-foreground">
                      {pond.depth_m === null
                        ? "Not recorded"
                        : `${pond.depth_m} m`}
                    </strong>
                  </span>

                  <span>
                    Species:{" "}
                    <strong className="text-foreground">
                      {pond.species?.common_name ??
                        "Not recorded"}
                    </strong>
                  </span>
                </>
              );
            })()}

          </div>
        </div>
      )}

      {dataError && (
        <div className="mt-4 rounded-xl border border-border bg-muted/30 px-4 py-3 text-xs text-foreground">
          {dataError}
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <PredictionField
          label="Pond area"
          unit="m²"
          value={form.pond_area_m2}
          onChange={(value) =>
            updateField(
              "pond_area_m2",
              value,
            )
          }
        />

        <PredictionField
          label="Pond depth"
          unit="m"
          value={form.pond_depth_m}
          onChange={(value) =>
            updateField(
              "pond_depth_m",
              value,
            )
          }
        />

        <PredictionField
          label="Stocking count"
          unit="shrimp"
          value={form.stocking_count}
          onChange={(value) =>
            updateField(
              "stocking_count",
              value,
            )
          }
        />

        <PredictionField
          label="Initial weight"
          unit="g"
          value={form.initial_average_weight_g}
          onChange={(value) =>
            updateField(
              "initial_average_weight_g",
              value,
            )
          }
        />

        <PredictionField
          label="Culture days"
          unit="days"
          value={form.culture_days}
          onChange={(value) =>
            updateField(
              "culture_days",
              value,
            )
          }
        />

        <PredictionField
          label="Survival rate"
          unit="0–1"
          value={form.survival_rate}
          step="0.01"
          onChange={(value) =>
            updateField(
              "survival_rate",
              value,
            )
          }
        />

        <PredictionField
          label="Growth rate"
          unit="g/week"
          value={form.growth_rate_g_week}
          step="0.01"
          onChange={(value) =>
            updateField(
              "growth_rate_g_week",
              value,
            )
          }
        />

        <div className="flex items-end">

          <button
            type="button"
            onClick={handlePredict}
            disabled={loading}
            className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-foreground px-4 text-xs font-semibold text-background transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4" />
            )}

            {loading
              ? "Predicting..."
              : "Predict production"}

          </button>

        </div>

      </div>


      {error && (
        <div className="mt-4 rounded-xl border border-border bg-muted/40 px-4 py-3 text-xs text-foreground">
          {error}
        </div>
      )}


      {result && (
        <div className="mt-5 grid gap-4 rounded-2xl border border-border bg-muted/30 p-4 sm:grid-cols-[1.2fr_1fr]">

          <div>

            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Predicted production
            </p>

            <div className="mt-2 flex items-end gap-2">

              <span className="text-3xl font-bold tracking-tight">

                {result.predicted_production_kg === null
                  ? "—"
                  : result.predicted_production_kg.toLocaleString(
                      undefined,
                      {
                        maximumFractionDigits: 1,
                      },
                    )}

              </span>

              <span className="pb-1 text-sm text-muted-foreground">
                kg
              </span>

            </div>

            <p className="mt-2 text-[11px] leading-5 text-muted-foreground">
              Model-generated estimate for the supplied
              operating assumptions.
            </p>

          </div>


          <div className="grid grid-cols-2 gap-3 sm:grid-cols-2">

            <ResultMeta
              label="Model"
              value={
                result.model_name ??
                "Unknown"
              }
            />

            <ResultMeta
              label="Version"
              value={
                result.model_version ??
                "Unknown"
              }
            />

            <ResultMeta
              label="Data basis"
              value="Synthetic"
            />

            <ResultMeta
              label="Validated"
              value="No"
            />

          </div>

        </div>
      )}

      <div className="mt-4 flex items-center gap-2 text-[10px] leading-4 text-muted-foreground">

        <TrendingUp className="h-3.5 w-3.5 shrink-0" />

        <span>
          Current model is trained on synthetic scenarios and
          has not been real-world validated.
        </span>

      </div>

    </section>
  );
}


function PredictionSelect({
  label,
  value,
  disabled,
  placeholder,
  options,
  onChange,
}: {
  label: string;
  value: string;
  disabled?: boolean;
  placeholder: string;
  options: {
    value: string;
    label: string;
  }[];
  onChange: (value: string) => void;
}) {

  return (
    <label className="block">

      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </span>

      <select
        value={value}
        disabled={disabled}
        onChange={(event) =>
          onChange(
            event.target.value,
          )
        }
        className="mt-1.5 h-11 w-full rounded-xl border border-border bg-background px-3 text-xs outline-none disabled:cursor-not-allowed disabled:opacity-50"
      >

        {!value && (
          <option value="">
            {placeholder}
          </option>
        )}

        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
          >
            {option.label}
          </option>
        ))}

      </select>

    </label>
  );
}


function PredictionField({
  label,
  unit,
  value,
  step = "any",
  onChange,
}: {
  label: string;
  unit: string;
  value: string;
  step?: string;
  onChange: (value: string) => void;
}) {

  return (
    <label className="block">

      <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </span>

      <div className="mt-1.5 flex items-center overflow-hidden rounded-xl border border-border bg-background">

        <input
          type="number"
          value={value}
          step={step}
          onChange={(event) =>
            onChange(
              event.target.value,
            )
          }
          className="h-11 min-w-0 flex-1 bg-transparent px-3 text-xs outline-none"
        />

        <span className="px-3 text-[9px] font-semibold text-muted-foreground">
          {unit}
        </span>

      </div>

    </label>
  );
}


function ResultMeta({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div className="rounded-xl border border-border bg-background p-3">

      <p className="text-[9px] uppercase tracking-wider text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 text-[11px] font-semibold">
        {value}
      </p>

    </div>
  );
}
