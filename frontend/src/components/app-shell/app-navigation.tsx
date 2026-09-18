"use client";

import {
  BrainCircuit,
  Droplets,
  Gauge,
  Home,
  Settings2,
  Waves,
} from "lucide-react";

import Link from "next/link";
import { usePathname } from "next/navigation";

const sections = [
  {
    title: "Workspace",
    items: [
      {
        label: "Dashboard",
        href: "/dashboard",
        icon: Home,
      },
      {
        label: "Farm setup",
        href: "/onboarding",
        icon: Waves,
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        label: "Water Quality",
        href: "/water-quality",
        icon: Droplets,
      },
    ],
  },
  {
    title: "Intelligence",
    items: [
      {
        label: "Forecasts",
        href: "/forecast",
        icon: Gauge,
      },
      {
        label: "Models",
        href: "/models",
        icon: BrainCircuit,
      },
      {
        label: "Aqua AI",
        href: "/ai",
        icon: BrainCircuit,
      },
    ],
  },
  {
    title: "System",
    items: [
      {
        label: "Platform",
        href: "/",
        icon: Settings2,
      },
    ],
  },
];

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <nav className="space-y-6">
      {sections.map((section) => (
        <section key={section.title}>
          <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            {section.title}
          </p>

          <div className="mt-2 space-y-1">
            {section.items.map((item) => {
              const Icon = item.icon;

              const active =
                pathname === item.href ||
                (
                  item.href !== "/" &&
                  pathname.startsWith(`${item.href}/`)
                );

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={[
                    "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition",
                    active
                      ? "bg-foreground font-semibold text-background"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  ].join(" ")}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>

                  {item.label === "Models" && (
                    <span
                      className={[
                        "ml-auto rounded-full px-1.5 py-0.5 text-[9px] font-semibold",
                        active
                          ? "bg-background/15"
                          : "bg-muted",
                      ].join(" ")}
                    >
                      ML
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </section>
      ))}
    </nav>
  );
}
