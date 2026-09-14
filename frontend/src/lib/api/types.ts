export type MeFarm = {
  id: string;
  name: string;
  location: string | null;
  farm_type: string | null;
  total_area_m2: number | null;
  water_source: string | null;
};

export type MeResponse = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farms: MeFarm[];
  farm_count: number;
};
