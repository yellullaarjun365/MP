import { apiFetch } from "./client";

export type Farm = {
  id: string;
  owner_id: string;
  name: string;
  location: string | null;
  farm_type: string | null;
  total_area_m2: number | null;
  water_source: string | null;
};

export function listFarms() {
  return apiFetch<Farm[]>("/api/v1/farms");
}
