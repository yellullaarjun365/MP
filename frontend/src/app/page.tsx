"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type MeResponse = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farm_count: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function Home() {
  const router = useRouter();
  const [message, setMessage] = useState("Checking your AquaLife session...");

  useEffect(() => {
    let active = true;

    async function resolveSession() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (!active) {
          return;
        }

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          setMessage("Unable to verify your session.");
          return;
        }

        const user =
          (await response.json()) as MeResponse;

        if (user.onboarding_status === "completed") {
          router.replace("/dashboard");
        } else {
          router.replace("/onboarding");
        }
      } catch {
        if (active) {
          router.replace("/login");
        }
      }
    }

    resolveSession();

    return () => {
      active = false;
    };
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-muted border-t-foreground" />
        <p className="mt-4 text-sm text-muted-foreground">
          {message}
        </p>
      </div>
    </main>
  );
}
