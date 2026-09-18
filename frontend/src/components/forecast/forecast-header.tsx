import {
  Clock3,
  Cpu,
  Waves,
} from "lucide-react";

type ForecastHeaderProps = {
  farmName: string | null;
  pondName: string | null;
};

export function ForecastHeader({
  farmName,
  pondName,
}: ForecastHeaderProps) {
  return (
    <section className="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-8">

      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">

        <div>

          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            <Waves className="h-4 w-4" />
            Forecast workspace
          </div>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            72-hour water forecast
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Compare recorded pond observations with future model output.
            Forecast values appear only when a connected forecasting service
            returns them.
          </p>

        </div>

        <div className="grid grid-cols-2 gap-3 sm:min-w-[320px]">

          <Meta
            icon={<Waves className="h-4 w-4" />}
            label="Farm"
            value={farmName ?? "Not selected"}
          />

          <Meta
            icon={<Cpu className="h-4 w-4" />}
            label="Pond"
            value={pondName ?? "Not selected"}
          />

        </div>

      </div>

      <div className="mt-6 flex flex-wrap items-center gap-2 text-xs">

        <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5">
          <span className="h-2 w-2 rounded-full bg-foreground" />
          Observed
        </span>

        <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-muted-foreground">
          <span className="h-2 w-2 rounded-full border border-current" />
          Forecast unavailable
        </span>

        <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-muted-foreground">
          <Clock3 className="h-3.5 w-3.5" />
          Horizon: 72 hours
        </span>

      </div>

    </section>
  );
}

function Meta({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-muted/20 p-4">

      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em]">
          {label}
        </p>
      </div>

      <p className="mt-2 truncate text-sm font-semibold">
        {value}
      </p>

    </div>
  );
}
