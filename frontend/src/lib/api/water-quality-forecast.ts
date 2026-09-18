export type ForecastPoint = {
  timestamp: string;
  value: number;
  lower?: number | null;
  upper?: number | null;
};

export type ObservedPoint = {
  timestamp: string;
  value: number;
};

export type WaterQualityForecast = {
  pond_id: string;
  target: string;
  unit: string;
  generated_at: string;
  horizon_hours: number;
  model_name: string | null;
  model_version: string | null;
  observed: ObservedPoint[];
  forecast: ForecastPoint[];
};
