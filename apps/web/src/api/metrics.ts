import { apiFetch } from "../lib/fetch";
import { MetricsOverview } from "../schemas/metrics";

export async function getOverview(hours?: number) {
  const qs = new URLSearchParams();
  if (hours) qs.set("hours", String(hours));
  const data = await apiFetch(`/metrics/overview?${qs.toString()}`);
  return MetricsOverview.parse(data);
}
