"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronRight,
  Home,
  LogIn,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Waves,
  X,
} from "lucide-react";

import { AppNavigation } from "@/components/app-shell/app-navigation";
import {
  AquaAIDrawer,
  AquaAIButton,
} from "@/components/ai/aqua-ai-drawer";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type User = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farm_count: number;
};

type AquaLifeShellProps = {
  children: React.ReactNode;
};

export function AquaLifeShell({
  children,
}: AquaLifeShellProps) {
  const pathname = usePathname();

  const sectionLabels: Record<string, string> = {
    "/dashboard": "Dashboard",
    "/forecast": "Forecasts",
    "/water-quality": "Water Quality",
    "/models": "Models",
    "/ai": "Aqua AI",
    "/onboarding": "Farm Setup",
  };

  const currentSection =
    sectionLabels[pathname] ??
    (pathname.startsWith("/models/") ? "Model detail" : "Workspace");

  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopSidebarOpen, setDesktopSidebarOpen] = useState(true);
  const [aquaAIOpen, setAquaAIOpen] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadSession() {
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

        if (response.ok) {
          const data = (await response.json()) as User;
          setUser(data);
        }
      } catch {
        // Anonymous mode is valid.
      } finally {
        if (active) {
          setCheckingAuth(false);
        }
      }
    }

    void loadSession();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [children]);

  function signIn() {
    window.location.href =
      `${API_URL}/api/v1/auth/google`;
  }

  async function logout() {
    try {
      await fetch(
        `${API_URL}/api/v1/auth/logout`,
        {
          method: "POST",
          credentials: "include",
          cache: "no-store",
        },
      );
    } finally {
      window.location.href = "/";
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">

        {desktopSidebarOpen && (
          <aside className="hidden w-64 shrink-0 border-r border-border/70 bg-background lg:flex lg:flex-col">
          <div className="relative flex h-16 shrink-0 items-center border-b border-border/70 px-5">
            <button
              type="button"
              aria-label="Close sidebar"
              title="Close sidebar"
              onClick={() => setDesktopSidebarOpen(false)}
              className="absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg border border-border text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <PanelLeftClose className="h-4 w-4" />
            </button>
            <Link
              href="/"
              className="flex items-center gap-2.5"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
                <Waves className="h-5 w-5" />
              </div>

              <div>
                <p className="text-sm font-bold tracking-tight">
                  AquaLife
                </p>

                <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Aquaculture intelligence
                </p>
              </div>
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto px-3 py-5">
            <Link
              href="/"
              className="mb-5 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>

            <AppNavigation />
          </div>

          <div className="border-t border-border/70 p-4">
            <button
              type="button"
              onClick={() => setAquaAIOpen(true)}
              className="flex w-full items-center gap-3 rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-left transition hover:bg-muted"
            >
              <Sparkles className="h-4 w-4" />
              <span className="text-xs font-semibold">
                Ask Aqua AI
              </span>
            </button>
          </div>

          <div className="border-t border-border/70 p-3">
            {checkingAuth ? (
              <div className="h-14 animate-pulse rounded-xl bg-muted" />
            ) : user ? (
              <div className="rounded-2xl border border-border bg-muted/30 p-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-foreground text-xs font-bold text-background">
                    {(user.full_name ?? user.email)
                      .slice(0, 1)
                      .toUpperCase()}
                  </div>

                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold">
                      {user.full_name ?? "AquaLife user"}
                    </p>

                    <p className="truncate text-[10px] text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => void logout()}
                  className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-border px-3 py-2 text-[11px] font-semibold text-muted-foreground transition hover:bg-background hover:text-foreground"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Log out
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={signIn}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-foreground px-3 py-2.5 text-xs font-semibold text-background transition hover:opacity-90"
              >
                <LogIn className="h-4 w-4" />
                Sign in with Google
              </button>
            )}
          </div>
          </aside>
        )}

        {!desktopSidebarOpen && (
          <button
            type="button"
            aria-label="Open sidebar"
            title="Open sidebar"
            onClick={() => setDesktopSidebarOpen(true)}
            className="fixed left-4 top-20 z-40 hidden h-10 w-10 items-center justify-center rounded-xl border border-border bg-background/95 text-foreground shadow-lg backdrop-blur lg:flex"
          >
            <PanelLeftOpen className="h-4 w-4" />
          </button>
        )}

        <div className="min-w-0 flex-1">
          <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border/70 bg-background/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                aria-label="Open navigation"
                onClick={() => setMobileOpen(true)}
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-border lg:hidden"
              >
                <Menu className="h-4 w-4" />
              </button>

              <Link
                href="/"
                className="flex shrink-0 items-center gap-2 lg:hidden"
              >
                <Waves className="h-5 w-5" />
                <span className="text-sm font-bold">
                  AquaLife
                </span>
              </Link>

              <div className="hidden min-w-0 items-center gap-2 text-xs sm:flex">
                <Link
                  href="/"
                  className="flex shrink-0 items-center gap-1.5 text-muted-foreground transition hover:text-foreground"
                >
                  <Home className="h-3.5 w-3.5" />
                  <span>Home</span>
                </Link>

                <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground/50" />

                <span className="truncate font-semibold text-foreground">
                  {currentSection}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <ThemeToggle />

              {!checkingAuth && user ? (
                <div className="hidden rounded-full border border-border px-3 py-1.5 text-xs font-semibold sm:block">
                  {user.full_name ?? user.email}
                </div>
              ) : null}
            </div>
          </header>

          <main className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            {children}
          </main>

          <AquaAIButton
            onClick={() => setAquaAIOpen(true)}
          />

          <AquaAIDrawer
            open={aquaAIOpen}
            onClose={() => setAquaAIOpen(false)}
          />
        </div>
      </div>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
            className="absolute inset-0 bg-black/40"
          />

          <aside className="relative flex h-full w-72 max-w-[85vw] flex-col border-r border-border bg-background shadow-2xl">
            <div className="flex h-16 items-center justify-between border-b border-border px-4">
              <Link
                href="/"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2.5"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
                  <Waves className="h-5 w-5" />
                </div>

                <span className="text-sm font-bold">
                  AquaLife
                </span>
              </Link>

              <button
                type="button"
                aria-label="Close navigation"
                onClick={() => setMobileOpen(false)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-border"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-3 py-5">
              <Link
                href="/"
                onClick={() => setMobileOpen(false)}
                className="mb-5 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground"
              >
                <Home className="h-4 w-4" />
                <span>Home</span>
              </Link>

              <div onClick={() => setMobileOpen(false)}>
                <AppNavigation />
              </div>
            </div>

            <div className="border-t border-border p-3">
              {user ? (
                <button
                  type="button"
                  onClick={() => void logout()}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-border px-3 py-2.5 text-xs font-semibold"
                >
                  <LogOut className="h-4 w-4" />
                  Log out
                </button>
              ) : (
                <button
                  type="button"
                  onClick={signIn}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-foreground px-3 py-2.5 text-xs font-semibold text-background"
                >
                  <LogIn className="h-4 w-4" />
                  Sign in with Google
                </button>
              )}
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
