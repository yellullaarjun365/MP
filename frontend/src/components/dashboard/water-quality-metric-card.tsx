import {
  Activity,
  Droplets,
  Gauge,
  Thermometer,
} from "lucide-react";


type MetricCardProps = {
  label: string;

  value: number | null;

  unit: string;

  measuredAt?: string | null;

  icon: React.ReactNode;
};


export function WaterQualityMetricCard({
  label,
  value,
  unit,
  measuredAt,
  icon,
}: MetricCardProps) {

  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">

      <div className="flex items-start justify-between gap-3">

        <div className="rounded-xl bg-muted p-2">
          {icon}
        </div>

        {value !== null && (
          <span className="rounded-full border border-border px-2 py-1 text-[10px] font-semibold text-muted-foreground">
            Observed
          </span>
        )}

      </div>

      <p className="mt-5 text-sm font-semibold">
        {label}
      </p>

      <div className="mt-2 flex items-baseline gap-2">

        <span className="text-2xl font-semibold tracking-tight">
          {value === null
            ? "—"
            : formatValue(value)}
        </span>

        <span className="text-xs text-muted-foreground">
          {unit}
        </span>

      </div>

      <p className="mt-2 text-[11px] leading-4 text-muted-foreground">
        {measuredAt
          ? `Measured ${formatDate(measuredAt)}`
          : "No measurement available"}
      </p>

    </div>
  );
}


function formatValue(
  value: number,
) {

  if (
    Number.isInteger(value)
  ) {
    return String(value);
  }

  return value.toFixed(2);
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


export function parameterIcon(
  parameter: string,
) {

  const normalized =
    parameter.trim().toLowerCase();

  if (
    normalized.includes("oxygen") ||
    normalized === "do"
  ) {
    return (
      <Droplets className="h-5 w-5" />
    );
  }

  if (
    normalized.includes("temperature")
  ) {
    return (
      <Thermometer className="h-5 w-5" />
    );
  }

  if (
    normalized === "ph" ||
    normalized.includes("ph")
  ) {
    return (
      <Gauge className="h-5 w-5" />
    );
  }

  return (
    <Activity className="h-5 w-5" />
  );
}
