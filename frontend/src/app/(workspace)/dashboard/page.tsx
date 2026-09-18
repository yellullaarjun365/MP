"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Dashboard } from "@/components/dashboard/dashboard";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function DashboardPage() {

  const router = useRouter();

  const [ready, setReady] =
    useState(false);


  useEffect(() => {

    let cancelled = false;

    async function verify() {

      try {

        const response =
          await fetch(
            `${API_URL}/api/v1/farms`,
            {
              credentials: "include",
              cache: "no-store",
            },
          );


        if (
          response.status === 401 ||
          response.status === 403
        ) {
          router.replace("/");
          return;
        }


        if (!response.ok) {
          throw new Error(
            `Authentication check failed: ${response.status}`,
          );
        }


        if (!cancelled) {
          setReady(true);
        }

      } catch {

        if (!cancelled) {
          router.replace("/");
        }

      }

    }


    void verify();


    return () => {
      cancelled = true;
    };

  }, [router]);


  if (!ready) {

    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6">

        <p className="text-sm text-muted-foreground">
          Loading AquaLife...
        </p>

      </div>
    );

  }


  return <Dashboard />;
}