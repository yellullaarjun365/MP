import { apiFetch } from "./client";

export type Pond = {
  id: string;
  farm_id: string;
  species_id: string | null;
  name: string;
  area_m2: number | null;
  depth_m: number | null;
  culture_type: string | null;
  water_source: string | null;
  species?: {
    id: string;
    common_name: string;
    scientific_name: string | null;
    category: string | null;
    is_active: boolean;
  } | null;
};

export function listFarmPonds(farmId: string) {
  return apiFetch<{
    value: Pond[];
    Count: number;
  }>(`/api/v1/ponds/farm/${farmId}`);
}
