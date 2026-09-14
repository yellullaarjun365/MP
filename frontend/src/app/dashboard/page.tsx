"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    async function verify() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (response.status === 401) {
          router.replace("/");
        }
      } catch {
        router.replace("/");
      }
    }

    verify();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-sm text-muted-foreground">
        Loading AquaLife...
      </p>
    </main>
  );
}
