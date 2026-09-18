import { apiFetch } from "./client";

export type ProductionPredictionInput = {
  species?: string | null;

  pond_area_m2?: number | null;

  pond_depth_m?: number | null;

  stocking_count?: number | null;

  stocking_density_per_m2?: number | null;

  initial_average_weight_g?: number | null;

  initial_biomass_kg?: number | null;

  temperature_c?: number | null;

  ph?: number | null;

  dissolved_oxygen_mg_l?: number | null;

  ammonia_mg_l?: number | null;

  nitrite_mg_l?: number | null;

  salinity_ppt?: number | null;

  feed_kg_day?: number | null;

  feed_frequency?: number | null;

  water_exchange_rate?: number | null;

  culture_days?: number | null;

  survival_rate?: number | null;

  growth_rate_g_week?: number | null;

  mortality_rate?: number | null;
};


export type PredictionRange = {
  lower?: number | null;

  upper?: number | null;
};


export type ProductionPredictionOutput = {
  target: "production_kg";

  predicted_production_kg:
    number | null;

  uncertainty:
    PredictionRange | null;

  confidence:
    number | null;

  model_name:
    string | null;

  model_version:
    string | null;

  feature_schema_version:
    string;

  generated_at:
    string;
};


export async function predictProduction(
  input: ProductionPredictionInput,
): Promise<ProductionPredictionOutput> {

  return apiFetch<ProductionPredictionOutput>(
    "/api/v1/prediction/production",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(input),
    },
  );
}
