import { apiFetch } from "./client";
import type { MeResponse } from "./types";

export function getMe() {
  return apiFetch<MeResponse>("/api/v1/me");
}
