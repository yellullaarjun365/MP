"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Dashboard } from "@/components/dashboard/dashboard";

type MeResponse = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farms: unknown[];
  farm_count: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadUser() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            method: "GET",
            credentials: "include",
            cache: "no-store",
          },
        );

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          throw new Error(
            `Authentication request failed (${response.status})`,
          );
        }

        const data =
          (await response.json()) as MeResponse;

        if (!active) {
          return;
        }

        setUser(data);

        if (data.onboarding_status !== "completed") {
          router.replace("/onboarding");
          return;
        }
      } catch (err) {
        if (!active) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load your account.",
        );
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
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-muted border-t-foreground" />
          <p className="mt-4 text-sm text-muted-foreground">
            Loading your AquaLife workspace...
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="max-w-md rounded-2xl border border-border bg-card p-6 text-center shadow-sm">
          <h1 className="text-lg font-semibold">
            Unable to load AquaLife
          </h1>

          <p className="mt-2 text-sm text-muted-foreground">
            {error}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-5 rounded-xl bg-foreground px-4 py-2 text-sm font-semibold text-background"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return <Dashboard />;
}
