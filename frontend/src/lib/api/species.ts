import { apiFetch } from "./client";

export type Species = {
  id: string;
  common_name: string;
  scientific_name: string | null;
  category: string | null;
  is_active: boolean;
};

export function listSpecies() {
  return apiFetch<{
    value: Species[];
    Count: number;
  }>("/api/v1/species");
}
