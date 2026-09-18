import {
  Activity,
  Droplets,
  Gauge,
  Thermometer,
} from "lucide-react";

type Props = {
  label: string;
  value: number | null;
  unit: string;
  timestamp: string | null;
};

export function ForecastMetricCard({
  label,
  value,
  unit,
  timestamp,
}: Props) {

  const Icon =
    label === "Dissolved oxygen"
      ? Droplets
      : label === "pH"
        ? Gauge
        : label === "Temperature"
          ? Thermometer
          : Activity;

  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between gap-3">

        <div className="rounded-xl bg-muted p-2">
          <Icon className="h-5 w-5" />
        </div>

        <span className="rounded-full border border-border px-2 py-1 text-[10px] font-semibold text-muted-foreground">
          Observed
        </span>

      </div>

      <p className="mt-5 text-sm font-semibold">
        {label}
      </p>

      <div className="mt-2 flex items-baseline gap-2">

        <span className="text-2xl font-semibold tracking-tight">
          {value === null ? "—" : format(value)}
        </span>

        <span className="text-xs text-muted-foreground">
          {unit}
        </span>

      </div>

      <p className="mt-2 text-[11px] text-muted-foreground">
        {timestamp
          ? formatTimestamp(timestamp)
          : "No recorded observation"}
      </p>

    </div>
  );
}

function format(value: number) {
  return Number.isInteger(value)
    ? String(value)
    : value.toFixed(2);
}

function formatTimestamp(value: string) {

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
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
