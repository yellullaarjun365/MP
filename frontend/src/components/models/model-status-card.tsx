import {
  CheckCircle2,
  Clock3,
  Database,
  Sparkles,
} from "lucide-react";

type ModelState =
  | "VERIFIED"
  | "PENDING"
  | "CONTRACT_READY";

type ModelStatusCardProps = {
  name: string;
  type: string;
  state: ModelState;
  fleetRmse?: number | null;
  description: string;
};

function stateLabel(state: ModelState) {
  if (state === "VERIFIED") {
    return "Verified";
  }

  if (state === "CONTRACT_READY") {
    return "Ready";
  }

  return "Pending";
}

function StateIcon({ state }: { state: ModelState }) {
  if (state === "VERIFIED") {
    return (
      <CheckCircle2 className="h-4 w-4" />
    );
  }

  if (state === "CONTRACT_READY") {
    return (
      <Sparkles className="h-4 w-4" />
    );
  }

  return (
    <Clock3 className="h-4 w-4" />
  );
}

export function ModelStatusCard({
  name,
  type,
  state,
  fleetRmse,
  description,
}: ModelStatusCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold">
            {name}
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            {type}
          </p>
        </div>

        <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/30 px-2.5 py-1 text-[10px] font-semibold">
          <StateIcon state={state} />
          {stateLabel(state)}
        </span>
      </div>

      <p className="mt-4 text-xs leading-5 text-muted-foreground">
        {description}
      </p>

      <div className="mt-5 flex items-end justify-between border-t border-border pt-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Fleet RMSE
          </p>

          <p className="mt-1 text-xl font-semibold tracking-tight">
            {fleetRmse == null
              ? "—"
              : fleetRmse.toFixed(4)}
            {fleetRmse != null && (
              <span className="ml-1 text-xs font-normal text-muted-foreground">
                mg/L
              </span>
            )}
          </p>
        </div>

        <Database className="h-5 w-5 text-muted-foreground" />
      </div>
    </div>
  );
}
