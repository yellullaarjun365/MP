"use client";

import { useEffect, useState } from "react";
import {
  ChevronDown,
  Loader2,
  MapPin,
  Waves,
} from "lucide-react";

import {
  listFarms,
  type Farm,
} from "@/lib/api/farms";

import {
  listFarmPonds,
  type Pond,
} from "@/lib/api/ponds";


type FarmPondSelectorProps = {
  onFarmChange?: (farm: Farm | null) => void;
  onPondChange?: (pond: Pond | null) => void;
};


export function FarmPondSelector({
  onFarmChange,
  onPondChange,
}: FarmPondSelectorProps) {

  const [farms, setFarms] = useState<Farm[]>([]);
  const [ponds, setPonds] = useState<Pond[]>([]);

  const [selectedFarmId, setSelectedFarmId] =
    useState<string>("");

  const [selectedPondId, setSelectedPondId] =
    useState<string>("");

  const [loadingFarms, setLoadingFarms] =
    useState(true);

  const [loadingPonds, setLoadingPonds] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const selectedFarm =
    farms.find(
      (farm) =>
        farm.id === selectedFarmId,
    ) ?? null;


  const selectedPond =
    ponds.find(
      (pond) =>
        pond.id === selectedPondId,
    ) ?? null;


  useEffect(() => {

    let cancelled = false;

    async function load() {

      setLoadingFarms(true);
      setError(null);

      try {

        const result =
          await listFarms();

        if (cancelled) {
          return;
        }

        setFarms(result);

        if (result.length > 0) {

          setSelectedFarmId(
            result[0].id,
          );
        }

      } catch {

        if (!cancelled) {
          setError(
            "Unable to load farms.",
          );
        }

      } finally {

        if (!cancelled) {
          setLoadingFarms(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };

  }, []);


  useEffect(() => {

    if (!selectedFarmId) {

      setPonds([]);
      setSelectedPondId("");

      onFarmChange?.(null);
      onPondChange?.(null);

      return;
    }


    onFarmChange?.(
      selectedFarm,
    );


    let cancelled = false;

    async function loadPonds() {

      setLoadingPonds(true);
      setError(null);

      try {

        const response =
          await listFarmPonds(
            selectedFarmId,
          );

        if (cancelled) {
          return;
        }

        const values =
          Array.isArray(response)
            ? response
            : response.value ?? [];

        setPonds(values);

        if (values.length > 0) {

          setSelectedPondId(
            values[0].id,
          );

        } else {

          setSelectedPondId("");

        }

      } catch {

        if (!cancelled) {
          setPonds([]);
          setSelectedPondId("");

          setError(
            "Unable to load ponds for this farm.",
          );
        }

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

  }, [
    selectedFarmId,
  ]);


  useEffect(() => {

    onPondChange?.(
      selectedPond,
    );

  }, [
    selectedPond,
    onPondChange,
  ]);


  function handleFarmChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {

    setSelectedFarmId(
      event.target.value,
    );

    setSelectedPondId("");
  }


  function handlePondChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {

    setSelectedPondId(
      event.target.value,
    );
  }


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between gap-4">

        <div>

          <p className="text-sm font-semibold">
            Farm & pond
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Select the production site you want to inspect.
          </p>

        </div>

        <Waves className="h-5 w-5 text-muted-foreground" />

      </div>


      <div className="mt-5 grid gap-4 lg:grid-cols-2">

        <div>

          <label
            htmlFor="farm-selector"
            className="mb-2 block text-xs font-semibold"
          >
            Farm
          </label>

          <div className="relative">

            <select
              id="farm-selector"
              value={selectedFarmId}
              onChange={handleFarmChange}
              disabled={loadingFarms}
              className="w-full appearance-none rounded-xl border border-border bg-background px-3 py-3 pr-10 text-sm outline-none transition focus:ring-2 focus:ring-foreground/10"
            >

              {loadingFarms && (
                <option value="">
                  Loading farms...
                </option>
              )}

              {!loadingFarms &&
                farms.length === 0 && (
                  <option value="">
                    No farms available
                  </option>
                )}

              {farms.map((farm) => (
                <option
                  key={farm.id}
                  value={farm.id}
                >
                  {farm.name}
                </option>
              ))}

            </select>

            {loadingFarms ? (
              <Loader2 className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            ) : (
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            )}

          </div>

        </div>


        <div>

          <label
            htmlFor="pond-selector"
            className="mb-2 block text-xs font-semibold"
          >
            Pond
          </label>

          <div className="relative">

            <select
              id="pond-selector"
              value={selectedPondId}
              onChange={handlePondChange}
              disabled={
                loadingPonds ||
                ponds.length === 0
              }
              className="w-full appearance-none rounded-xl border border-border bg-background px-3 py-3 pr-10 text-sm outline-none transition focus:ring-2 focus:ring-foreground/10"
            >

              {loadingPonds && (
                <option value="">
                  Loading ponds...
                </option>
              )}

              {!loadingPonds &&
                ponds.length === 0 && (
                  <option value="">
                    No ponds available
                  </option>
                )}

              {ponds.map((pond) => (
                <option
                  key={pond.id}
                  value={pond.id}
                >
                  {pond.name}
                </option>
              ))}

            </select>

            {loadingPonds ? (
              <Loader2 className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            ) : (
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            )}

          </div>

        </div>

      </div>


      {error && (
        <div className="mt-4 rounded-xl border border-destructive/20 bg-destructive/5 px-3 py-2 text-xs text-destructive">
          {error}
        </div>
      )}

    </section>
  );
}


export function FarmPondSummary({
  farm,
  pond,
}: {
  farm: Farm | null;
  pond: Pond | null;
}) {

  if (!farm && !pond) {

    return (
      <div className="rounded-2xl border border-dashed border-border p-6 text-sm text-muted-foreground">
        Select a farm and pond to view details.
      </div>
    );
  }


  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

      <InfoCard
        label="Farm"
        value={
          farm?.name ??
          "—"
        }
        icon={
          <Waves className="h-4 w-4" />
        }
      />

      <InfoCard
        label="Location"
        value={
          farm?.location ??
          "Not available"
        }
        icon={
          <MapPin className="h-4 w-4" />
        }
      />

      <InfoCard
        label="Pond"
        value={
          pond?.name ??
          "—"
        }
        icon={
          <Waves className="h-4 w-4" />
        }
      />

      <InfoCard
        label="Species"
        value={
          pond?.species?.common_name ??
          "Not specified"
        }
        icon={
          <Waves className="h-4 w-4" />
        }
      />

    </section>
  );
}


function InfoCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {

  return (
    <div className="rounded-2xl border border-border bg-card p-4 shadow-sm">

      <div className="flex items-center gap-2 text-muted-foreground">

        {icon}

        <p className="text-[10px] font-semibold uppercase tracking-[0.16em]">
          {label}
        </p>

      </div>

      <p className="mt-3 truncate text-sm font-semibold">
        {value}
      </p>

    </div>
  );
}
