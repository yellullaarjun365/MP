"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  ChevronDown,
  Loader2,
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


type Props = {
  onPondChange?: (
    pond: Pond | null,
  ) => void;
};


export function DashboardFarmContext({
  onPondChange,
}: Props) {

  const [farms, setFarms] =
    useState<Farm[]>([]);

  const [ponds, setPonds] =
    useState<Pond[]>([]);

  const [farmId, setFarmId] =
    useState<string>("");

  const [pondId, setPondId] =
    useState<string>("");

  const [loadingFarms, setLoadingFarms] =
    useState(true);

  const [loadingPonds, setLoadingPonds] =
    useState(false);


  const selectedFarm =
    farms.find(
      (farm) =>
        farm.id === farmId,
    ) ?? null;


  const selectedPond =
    ponds.find(
      (pond) =>
        pond.id === pondId,
    ) ?? null;


  useEffect(() => {

    let cancelled = false;

    async function load() {

      try {

        const result =
          await listFarms();

        if (cancelled) {
          return;
        }

        setFarms(result);

        if (result.length > 0) {
          setFarmId(result[0].id);
        }

      } catch {
        if (!cancelled) {
          setFarms([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingFarms(false);
        }
      }

    }

    void load();

    return () => {
      cancelled = true;
    };

  }, []);


  useEffect(() => {

    if (!farmId) {
      setPonds([]);
      setPondId("");
      onPondChange?.(null);
      return;
    }


    let cancelled = false;

    async function load() {

      setLoadingPonds(true);

      try {

        const response =
          await listFarmPonds(
            farmId,
          );

        if (cancelled) {
          return;
        }

        const values =
          response.value ?? [];

        setPonds(values);

        if (values.length > 0) {
          setPondId(values[0].id);
        } else {
          setPondId("");
          onPondChange?.(null);
        }

      } catch {

        if (!cancelled) {
          setPonds([]);
          setPondId("");
          onPondChange?.(null);
        }

      } finally {

        if (!cancelled) {
          setLoadingPonds(false);
        }

      }

    }

    void load();

    return () => {
      cancelled = true;
    };

  }, [
    farmId,
    onPondChange,
  ]);


  useEffect(() => {

    onPondChange?.(
      selectedPond,
    );

  }, [
    selectedPond,
    onPondChange,
  ]);


  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start gap-3">

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-muted">

          <Waves className="h-4 w-4" />

        </div>

        <div>

          <p className="text-sm font-semibold">
            Active farm
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Choose the operating context for this dashboard.
          </p>

        </div>

      </div>


      <div className="mt-5 grid gap-3 md:grid-cols-2">

        <Selector
          label="Farm"
          value={farmId}
          onChange={setFarmId}
          disabled={loadingFarms}
          loading={loadingFarms}
          options={
            farms.map(
              (farm) => ({
                value: farm.id,
                label: farm.name,
              }),
            )
          }
        />


        <Selector
          label="Pond"
          value={pondId}
          onChange={setPondId}
          disabled={
            loadingPonds ||
            ponds.length === 0
          }
          loading={loadingPonds}
          options={
            ponds.map(
              (pond) => ({
                value: pond.id,
                label: pond.name,
              }),
            )
          }
        />

      </div>


      {selectedPond && (
        <div className="mt-4 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">

          <Context
            label="Location"
            value={
              selectedFarm?.location ??
              "Not specified"
            }
          />

          <Context
            label="Area"
            value={
              selectedPond.area_m2 !== null
                ? `${selectedPond.area_m2} m²`
                : "Not specified"
            }
          />

          <Context
            label="Depth"
            value={
              selectedPond.depth_m !== null
                ? `${selectedPond.depth_m} m`
                : "Not specified"
            }
          />

          <Context
            label="Species"
            value={
              selectedPond.species?.common_name ??
              "Not specified"
            }
          />

        </div>
      )}

    </section>
  );
}


function Selector({
  label,
  value,
  onChange,
  disabled,
  loading,
  options,
}: {
  label: string;
  value: string;
  onChange: (
    value: string,
  ) => void;
  disabled: boolean;
  loading: boolean;
  options: {
    value: string;
    label: string;
  }[];
}) {

  return (
    <div>

      <label className="mb-2 block text-xs font-semibold">
        {label}
      </label>

      <div className="relative">

        <select
          value={value}
          onChange={(event) =>
            onChange(
              event.target.value,
            )
          }
          disabled={disabled}
          className="w-full appearance-none rounded-xl border border-border bg-background px-3 py-3 pr-10 text-sm outline-none focus:ring-2 focus:ring-foreground/10 disabled:opacity-60"
        >

          {options.length === 0 && (
            <option value="">
              {loading
                ? "Loading..."
                : "No data available"}
            </option>
          )}

          {options.map(
            (option) => (
              <option
                key={option.value}
                value={option.value}
              >
                {option.label}
              </option>
            ),
          )}

        </select>

        {loading ? (
          <Loader2 className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin" />
        ) : (
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2" />
        )}

      </div>

    </div>
  );
}


function Context({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div className="rounded-xl border border-border bg-muted/20 p-3">

      <p className="text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 truncate text-xs font-semibold">
        {value}
      </p>

    </div>
  );
}