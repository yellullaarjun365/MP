"use client";

import {
  Activity,
  BarChart3,
  BrainCircuit,
  Droplets,
  Gauge,
  Home,
  Settings,
  Waves,
} from "lucide-react";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    label: "Farms",
    href: "/dashboard",
    icon: Waves,
  },
  {
    label: "Water Quality",
    href: "/water-quality",
    icon: Droplets,
  },
  {
    label: "Forecasts",
    href: "/forecast",
    icon: Gauge,
  },
  {
    label: "Production",
    href: "/dashboard",
    icon: Gauge,
  },
  {
    label: "Analytics",
    href: "/dashboard",
    icon: BarChart3,
  },
  {
    label: "Models",
    href: "/models",
    icon: BrainCircuit,
  },
  {
    label: "AI Assistant",
    href: "/ai",
    icon: Activity,
  },
];

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {items.map((item) => {
        const Icon = item.icon;

        const active =
          pathname === item.href ||
          (
            item.href !== "/dashboard" &&
            pathname.startsWith(item.href)
          );

        return (
          <Link
            key={item.label}
            href={item.href}
            className={[
              "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition",
              active
                ? "bg-foreground text-background"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            ].join(" ")}
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

      <div className="pt-4">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground"
        >
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </Link>
      </div>
    </nav>
  );
}

