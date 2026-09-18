import { apiFetch } from "./client";


export type WaterQualityMeasurement = {
  id: string;

  pond_id: string;

  parameter: string;

  value: number;

  unit: string;

  measured_at: string;

  source: string;
};


export function listWaterQuality(
  pondId: string,
) {
  return apiFetch<WaterQualityMeasurement[]>(
    `/api/v1/operations/water-quality/${pondId}`,
  );
}
