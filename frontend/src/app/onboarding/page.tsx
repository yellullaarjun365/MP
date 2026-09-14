"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Check,
  Fish,
  MapPin,
  Waves,
} from "lucide-react";

type User = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farm_count: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function OnboardingPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadUser() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          router.replace("/login");
          return;
        }

        const data = (await response.json()) as User;

        if (data.onboarding_status === "completed") {
          router.replace("/dashboard");
          return;
        }

        if (active) {
          setUser(data);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      active = false;
    };
  }, [router]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted border-t-foreground" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8 lg:px-10">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
              <Waves className="h-5 w-5" />
            </div>

            <div>
              <p className="text-sm font-bold">
                AquaLife
              </p>
              <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Setup workspace
              </p>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            {user?.email}
          </p>
        </header>

        <div className="mx-auto flex w-full max-w-4xl flex-1 items-center py-12">
          <div className="grid w-full gap-12 lg:grid-cols-[220px_1fr]">
            <aside>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Getting started
              </p>

              <div className="mt-6 space-y-4">
                {[
                  ["1", "Welcome"],
                  ["2", "Your farm"],
                  ["3", "Ponds"],
                ].map(([number, label]) => (
                  <div
                    key={number}
                    className="flex items-center gap-3"
                  >
                    <div
                      className={[
                        "flex h-8 w-8 items-center justify-center rounded-full border text-xs font-semibold",
                        Number(number) <= step
                          ? "border-foreground bg-foreground text-background"
                          : "border-border text-muted-foreground",
                      ].join(" ")}
                    >
                      {Number(number) < step ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        number
                      )}
                    </div>

                    <span
                      className={[
                        "text-sm",
                        Number(number) === step
                          ? "font-semibold"
                          : "text-muted-foreground",
                      ].join(" ")}
                    >
                      {label}
                    </span>
                  </div>
                ))}
              </div>
            </aside>

            <section className="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-10">
              {step === 1 && (
                <>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Welcome
                  </p>

                  <h1 className="mt-3 text-3xl font-bold tracking-tight">
                    Let's set up your AquaLife workspace.
                  </h1>

                  <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
                    We'll configure your farm and ponds first.
                    AquaLife will use this structure throughout
                    monitoring, analytics and AI recommendations.
                  </p>

                  <div className="mt-8 grid gap-3 sm:grid-cols-3">
                    <Feature
                      icon={MapPin}
                      title="Farm"
                      text="Location and production setup"
                    />

                    <Feature
                      icon={Waves}
                      title="Ponds"
                      text="Area, depth and water source"
                    />

                    <Feature
                      icon={Fish}
                      title="Species"
                      text="Production species"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="mt-10 flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background"
                  >
                    Start setup
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </>
              )}

              {step === 2 && (
                <>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Step 2
                  </p>

                  <h1 className="mt-3 text-3xl font-bold tracking-tight">
                    Tell us about your farm.
                  </h1>

                  <p className="mt-3 text-sm text-muted-foreground">
                    The actual farm creation form will be connected
                    to your onboarding API next.
                  </p>

                  <div className="mt-8 rounded-2xl border border-dashed border-border bg-muted/20 p-6">
                    <p className="text-sm font-semibold">
                      Farm configuration
                    </p>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                      Name, location, farm type, total area and
                      water source.
                    </p>
                  </div>

                  <div className="mt-8 flex justify-between">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="rounded-xl border border-border px-5 py-3 text-sm font-semibold"
                    >
                      Back
                    </button>

                    <button
                      type="button"
                      onClick={() => setStep(3)}
                      className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background"
                    >
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </>
              )}

              {step === 3 && (
                <>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Step 3
                  </p>

                  <h1 className="mt-3 text-3xl font-bold tracking-tight">
                    Configure your ponds.
                  </h1>

                  <p className="mt-3 text-sm text-muted-foreground">
                    Add ponds, assign species and define their
                    operating parameters.
                  </p>

                  <div className="mt-8 rounded-2xl border border-dashed border-border bg-muted/20 p-6">
                    <p className="text-sm font-semibold">
                      Pond configuration
                    </p>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                      Pond creation will use the existing transactional
                      onboarding API.
                    </p>
                  </div>

                  <div className="mt-8 flex justify-between">
                    <button
                      type="button"
                      onClick={() => setStep(2)}
                      className="rounded-xl border border-border px-5 py-3 text-sm font-semibold"
                    >
                      Back
                    </button>

                    <button
                      type="button"
                      onClick={() => router.replace("/dashboard")}
                      className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background"
                    >
                      Finish preview
                      <Check className="h-4 w-4" />
                    </button>
                  </div>
                </>
              )}
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}

function Feature({
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
      <Icon className="h-4 w-4" />
      <p className="mt-3 text-xs font-semibold">{title}</p>
      <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}
