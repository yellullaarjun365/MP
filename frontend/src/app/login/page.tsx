"use client";

import { useEffect } from "react";

export default function LoginPage() {
  useEffect(() => {
    window.location.replace("/");
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-sm text-muted-foreground">
        Opening AquaLife...
      </p>
    </main>
  );
}
