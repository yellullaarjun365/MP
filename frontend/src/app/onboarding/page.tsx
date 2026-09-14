"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Droplets,
  Fish,
  Plus,
  Trash2,
  Waves,
} from "lucide-react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type Species = {
  id: string;
  common_name: string;
  scientific_name: string | null;
  category: string | null;
  is_active: boolean;
};

type PondForm = {
  name: string;
  species_id: string;
  area_m2: string;
  depth_m: string;
  culture_type: string;
  water_source: string;
};

const emptyPond = (): PondForm => ({
  name: "",
  species_id: "",
  area_m2: "",
  depth_m: "",
  culture_type: "Grow-out",
  water_source: "Groundwater",
});

export default function OnboardingPage() {
  const router = useRouter();

  const [step, setStep] = useState(1);

  const [farmName, setFarmName] = useState("");
  const [location, setLocation] = useState("");
  const [farmType, setFarmType] = useState("Shrimp Aquaculture");
  const [totalArea, setTotalArea] = useState("");
  const [farmWaterSource, setFarmWaterSource] =
    useState("Groundwater");

  const [species, setSpecies] = useState<Species[]>([]);
  const [ponds, setPonds] = useState<PondForm[]>([
    emptyPond(),
  ]);

  const [loadingSpecies, setLoadingSpecies] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    async function loadSpecies() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/species`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (!response.ok) {
          throw new Error("Unable to load species.");
        }

        const data = await response.json();

        const available =
          Array.isArray(data)
            ? data
            : Array.isArray(data.value)
              ? data.value
              : [];

        setSpecies(
          available.filter(
            (item: Species) => item.is_active,
          ),
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load species.",
        );
      } finally {
        setLoadingSpecies(false);
      }
    }

    loadSpecies();
  }, []);

  function updatePond(
    index: number,
    field: keyof PondForm,
    value: string,
  ) {
    setPonds((current) =>
      current.map((pond, pondIndex) =>
        pondIndex === index
          ? {
              ...pond,
              [field]: value,
            }
          : pond,
      ),
    );
  }

  function addPond() {
    setPonds((current) => [
      ...current,
      emptyPond(),
    ]);
  }

  function removePond(index: number) {
    setPonds((current) =>
      current.length === 1
        ? current
        : current.filter(
            (_, pondIndex) =>
              pondIndex !== index,
          ),
    );
  }

  function validateFarm() {
    if (!farmName.trim()) {
      setError("Enter your farm name.");
      return false;
    }

    if (!location.trim()) {
      setError("Enter the farm location.");
      return false;
    }

    if (!totalArea || Number(totalArea) <= 0) {
      setError("Enter a valid total farm area.");
      return false;
    }

    return true;
  }

  function validatePonds() {
    for (let index = 0; index < ponds.length; index += 1) {
      const pond = ponds[index];

      if (!pond.name.trim()) {
        setError(`Enter a name for Pond ${index + 1}.`);
        return false;
      }

      if (!pond.species_id) {
        setError(
          `Select a species for Pond ${index + 1}.`,
        );
        return false;
      }

      if (!pond.area_m2 || Number(pond.area_m2) <= 0) {
        setError(
          `Enter a valid area for Pond ${index + 1}.`,
        );
        return false;
      }

      if (!pond.depth_m || Number(pond.depth_m) <= 0) {
        setError(
          `Enter a valid depth for Pond ${index + 1}.`,
        );
        return false;
      }
    }

    return true;
  }

  function nextFromWelcome() {
    setError("");
    setStep(2);
  }

  function nextFromFarm() {
    setError("");

    if (!validateFarm()) {
      return;
    }

    setStep(3);
  }

  function back() {
    setError("");

    setStep((current) =>
      Math.max(1, current - 1),
    );
  }

  async function submitOnboarding(
    event?: FormEvent,
  ) {
    event?.preventDefault();

    setError("");

    if (!validateFarm()) {
      setStep(2);
      return;
    }

    if (!validatePonds()) {
      setStep(3);
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/onboarding/setup`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: farmName.trim(),
            location: location.trim(),
            farm_type: farmType.trim() || null,
            total_area_m2: Number(totalArea),
            water_source:
              farmWaterSource.trim() || null,
            ponds: ponds.map((pond) => ({
              name: pond.name.trim(),
              species_id: pond.species_id,
              area_m2: Number(pond.area_m2),
              depth_m: Number(pond.depth_m),
              culture_type:
                pond.culture_type.trim() || null,
              water_source:
                pond.water_source.trim() || null,
            })),
          }),
        },
      );

      const data = await response
        .json()
        .catch(() => ({}));

      if (response.status === 401) {
        router.replace("/");
        return;
      }

      if (!response.ok) {
        throw new Error(
          data.detail ??
            "Unable to create your farm setup.",
        );
      }

      setSuccess(true);

      setTimeout(() => {
        router.replace("/");
      }, 900);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create your farm setup.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="w-full max-w-md rounded-3xl border border-border bg-card p-8 text-center shadow-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-foreground text-background">
            <Check className="h-6 w-6" />
          </div>

          <h1 className="mt-5 text-2xl font-bold tracking-tight">
            Your AquaLife workspace is ready.
          </h1>

          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Your farm and pond configuration has been
            created successfully.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex items-center justify-between border-b border-border pb-5">
          <button
            type="button"
            onClick={() => router.replace("/")}
            className="flex items-center gap-3"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
              <Waves className="h-5 w-5" />
            </div>

            <div className="text-left">
              <p className="text-sm font-bold">
                AquaLife
              </p>

              <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Setup workspace
              </p>
            </div>
          </button>

          <span className="text-xs text-muted-foreground">
            Step {step} of 3
          </span>
        </header>

        <div className="mx-auto grid max-w-6xl gap-8 py-10 lg:grid-cols-[220px_1fr] lg:py-16">
          <aside>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Getting started
            </p>

            <div className="mt-6 space-y-5">
              {[
                ["1", "Welcome"],
                ["2", "Your farm"],
                ["3", "Ponds"],
              ].map(([number, label]) => {
                const numberValue = Number(number);
                const completed =
                  numberValue < step;
                const active =
                  numberValue === step;

                return (
                  <div
                    key={number}
                    className="flex items-center gap-3"
                  >
                    <div
                      className={[
                        "flex h-9 w-9 items-center justify-center rounded-full border text-xs font-semibold",
                        completed || active
                          ? "border-foreground bg-foreground text-background"
                          : "border-border text-muted-foreground",
                      ].join(" ")}
                    >
                      {completed ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        number
                      )}
                    </div>

                    <span
                      className={[
                        "text-sm",
                        active
                          ? "font-semibold"
                          : "text-muted-foreground",
                      ].join(" ")}
                    >
                      {label}
                    </span>
                  </div>
                );
              })}
            </div>
          </aside>

          <section className="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-10">
            {error && (
              <div className="mb-6 rounded-2xl border border-border bg-muted/40 px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {step === 1 && (
              <>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Welcome
                </p>

                <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                  Let's configure your AquaLife workspace.
                </h1>

                <p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground">
                  Tell AquaLife about your farm and ponds so
                  the platform can organize your operation and
                  prepare it for monitoring, analytics and AI.
                </p>

                <div className="mt-8 grid gap-4 md:grid-cols-3">
                  <InfoCard
                    icon={Droplets}
                    title="Farm"
                    text="Basic production and location information."
                  />

                  <InfoCard
                    icon={Waves}
                    title="Ponds"
                    text="Area, depth, water source and species."
                  />

                  <InfoCard
                    icon={Fish}
                    title="Intelligence"
                    text="Build the foundation for future AI insights."
                  />
                </div>

                <button
                  type="button"
                  onClick={nextFromWelcome}
                  className="mt-10 flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background"
                >
                  Start setup
                  <ArrowRight className="h-4 w-4" />
                </button>
              </>
            )}

            {step === 2 && (
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  nextFromFarm();
                }}
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Step 2
                </p>

                <h1 className="mt-3 text-3xl font-bold tracking-tight">
                  Tell us about your farm.
                </h1>

                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  These details help AquaLife understand the
                  scale and context of your operation.
                </p>

                <div className="mt-8 grid gap-5 sm:grid-cols-2">
                  <Field
                    label="Farm name"
                    value={farmName}
                    onChange={setFarmName}
                    placeholder="e.g. Krishna Aqua Farm"
                    required
                  />

                  <Field
                    label="Location"
                    value={location}
                    onChange={setLocation}
                    placeholder="e.g. Andhra Pradesh"
                    required
                  />

                  <Field
                    label="Farm type"
                    value={farmType}
                    onChange={setFarmType}
                    placeholder="e.g. Shrimp Aquaculture"
                  />

                  <Field
                    label="Total area (m²)"
                    value={totalArea}
                    onChange={setTotalArea}
                    placeholder="e.g. 4000"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                  />

                  <Field
                    label="Primary water source"
                    value={farmWaterSource}
                    onChange={setFarmWaterSource}
                    placeholder="e.g. Groundwater"
                  />
                </div>

                <div className="mt-10 flex justify-between">
                  <button
                    type="button"
                    onClick={back}
                    className="flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-sm font-semibold"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Back
                  </button>

                  <button
                    type="submit"
                    className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background"
                  >
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </form>
            )}

            {step === 3 && (
              <form onSubmit={submitOnboarding}>
                <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Step 3
                    </p>

                    <h1 className="mt-3 text-3xl font-bold tracking-tight">
                      Configure your ponds.
                    </h1>

                    <p className="mt-3 text-sm leading-6 text-muted-foreground">
                      Add as many ponds as you need and assign
                      the species being cultured.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={addPond}
                    className="flex items-center justify-center gap-2 rounded-xl border border-border px-4 py-2.5 text-xs font-semibold"
                  >
                    <Plus className="h-4 w-4" />
                    Add pond
                  </button>
                </div>

                <div className="mt-8 space-y-5">
                  {ponds.map((pond, index) => (
                    <div
                      key={index}
                      className="rounded-2xl border border-border p-5"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-semibold">
                            Pond {index + 1}
                          </p>

                          <p className="mt-1 text-[11px] text-muted-foreground">
                            Pond operating configuration
                          </p>
                        </div>

                        {ponds.length > 1 && (
                          <button
                            type="button"
                            onClick={() =>
                              removePond(index)
                            }
                            className="rounded-lg p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
                            aria-label={`Remove pond ${index + 1}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>

                      <div className="mt-5 grid gap-4 sm:grid-cols-2">
                        <Field
                          label="Pond name"
                          value={pond.name}
                          onChange={(value) =>
                            updatePond(
                              index,
                              "name",
                              value,
                            )
                          }
                          placeholder={`Pond ${index + 1}`}
                          required
                        />

                        <div>
                          <label className="text-xs font-medium">
                            Species
                          </label>

                          <select
                            value={pond.species_id}
                            onChange={(event) =>
                              updatePond(
                                index,
                                "species_id",
                                event.target.value,
                              )
                            }
                            disabled={loadingSpecies}
                            className="mt-2 h-11 w-full rounded-xl border border-border bg-background px-3 text-xs outline-none focus:ring-2 focus:ring-ring"
                            required
                          >
                            <option value="">
                              {loadingSpecies
                                ? "Loading species..."
                                : "Select species"}
                            </option>

                            {species.map((item) => (
                              <option
                                key={item.id}
                                value={item.id}
                              >
                                {item.common_name}
                              </option>
                            ))}
                          </select>
                        </div>

                        <Field
                          label="Area (m²)"
                          value={pond.area_m2}
                          onChange={(value) =>
                            updatePond(
                              index,
                              "area_m2",
                              value,
                            )
                          }
                          placeholder="1000"
                          type="number"
                          min="0"
                          step="0.01"
                          required
                        />

                        <Field
                          label="Depth (m)"
                          value={pond.depth_m}
                          onChange={(value) =>
                            updatePond(
                              index,
                              "depth_m",
                              value,
                            )
                          }
                          placeholder="1.5"
                          type="number"
                          min="0"
                          step="0.01"
                          required
                        />

                        <Field
                          label="Culture type"
                          value={pond.culture_type}
                          onChange={(value) =>
                            updatePond(
                              index,
                              "culture_type",
                              value,
                            )
                          }
                          placeholder="Grow-out"
                        />

                        <Field
                          label="Water source"
                          value={pond.water_source}
                          onChange={(value) =>
                            updatePond(
                              index,
                              "water_source",
                              value,
                            )
                          }
                          placeholder="Groundwater"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 rounded-2xl border border-dashed border-border bg-muted/20 p-4">
                  <p className="text-xs font-semibold">
                    Ready to create your workspace?
                  </p>

                  <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
                    AquaLife will create the farm and all configured
                    ponds in one transactional operation.
                  </p>
                </div>

                <div className="mt-8 flex justify-between">
                  <button
                    type="button"
                    onClick={back}
                    className="flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-sm font-semibold"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Back
                  </button>

                  <button
                    type="submit"
                    disabled={
                      submitting ||
                      loadingSpecies
                    }
                    className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background disabled:opacity-50"
                  >
                    {submitting
                      ? "Creating workspace..."
                      : "Create workspace"}

                    {!submitting && (
                      <Check className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </form>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  min,
  step,
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  min?: string;
  step?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="text-xs font-medium">
        {label}
      </label>

      <input
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        placeholder={placeholder}
        type={type}
        min={min}
        step={step}
        required={required}
        className="mt-2 h-11 w-full rounded-xl border border-border bg-background px-3 text-xs outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring"
      />
    </div>
  );
}

function InfoCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-border p-4">
      <Icon className="h-5 w-5" />

      <p className="mt-4 text-xs font-semibold">
        {title}
      </p>

      <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}
