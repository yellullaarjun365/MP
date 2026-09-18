import {
  BrainCircuit,
  Clock3,
} from "lucide-react";

export function ForecastUnavailable() {
  return (
    <section className="rounded-2xl border border-border bg-card shadow-sm">

      <div className="border-b border-border p-5">

        <div className="flex items-center gap-2">

          <BrainCircuit className="h-4 w-4" />

          <div>
            <p className="text-sm font-semibold">
              72-hour forecast
            </p>

            <p className="mt-1 text-xs text-muted-foreground">
              Future model output for the selected pond
            </p>
          </div>

        </div>

      </div>

      <div className="flex min-h-[300px] items-center justify-center p-8">

        <div className="max-w-md text-center">

          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-muted/20">
            <Clock3 className="h-5 w-5" />
          </div>

          <p className="mt-5 text-sm font-semibold">
            Forecast service not connected
          </p>

          <p className="mt-2 text-xs leading-5 text-muted-foreground">
            AquaLife has the forecast interface ready, but no verified
            72-hour water-quality forecast endpoint is currently supplying
            future values for this pond.
          </p>

          <p className="mt-4 text-[11px] leading-5 text-muted-foreground">
            No forecast points are generated or displayed here until the
            forecasting service provides them.
          </p>

        </div>

      </div>

    </section>
  );
}
