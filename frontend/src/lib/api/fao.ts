import { apiFetch } from "./client";

export type FaoYearlyProduction = {
  year: number;
  production_tonnes: number;
  production_kg: number;
  observations: number;
  environments: number;
  yoy_change_pct: number | null;
};

export type FaoEnvironmentBreakdown = {
  year: number;
  environment_code: string;
  environment: string;
  production_tonnes: number;
  production_kg: number;
  status: string | null;
};

export type FaoStatusBreakdown = {
  status: string;
  observations: number;
  production_tonnes: number;
  share_pct: number;
};

export type FaoSourceInformation = {
  provider: string | null;
  database: string | null;
  coverage: string | null;
  frequency: string | null;
  license: string | null;
  status: string | null;
};

export type FaoScientificBoundary = {
  source_type: string;
  real_world: boolean;
  pond_level: boolean;
  farm_level: boolean;
  synthetic: boolean;
  model_training: boolean;
  prediction_accuracy_claim: boolean;
  missing_years_interpolated: boolean;
  status_preserved: boolean;
};

export type FaoVannameiHistory = {
  country: "India";
  species: "Litopenaeus vannamei";
  source: "FAO";
  dataset: "Global Aquaculture Production";

  release: string;
  data_through: number;

  first_year: number;
  last_year: number;
  year_count: number;

  missing_years: number[];

  first_year_production_tonnes: number;
  last_year_production_tonnes: number;

  endpoint_growth_cagr_pct: number | null;

  official_observations: number;
  imputed_observations: number;

  yearly_production: FaoYearlyProduction[];
  environment_breakdown: FaoEnvironmentBreakdown[];
  status_breakdown: FaoStatusBreakdown[];

  source_information: FaoSourceInformation;
  scientific_boundary: FaoScientificBoundary;
};

export async function getIndiaVannameiHistory(): Promise<FaoVannameiHistory> {
  return apiFetch<FaoVannameiHistory>(
    "/api/v1/analytics/fao/india/vannamei",
    {
      method: "GET",
    },
  );
}
