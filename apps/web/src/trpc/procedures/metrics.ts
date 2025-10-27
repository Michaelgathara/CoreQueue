import { initTRPC } from "@trpc/server";
import { z } from "zod";
import { apiFetch } from "../../lib/fetch";

const t = initTRPC.create();

export const MetricsOverview = z.object({
  cpu_avg: z.number(),
  gpu_avg: z.number(),
  queue_time_avg_sec: z.number(),
  run_time_avg_sec: z.number(),
  violations: z.object({
    max_wall_time: z.number(),
    deny_if_device_thermal_state: z.number(),
    max_concurrent_gpu_jobs: z.number(),
  }),
});

export const metricsRouter = t.router({
  overview: t.procedure
    .input(z.object({ hours: z.number().optional() }).optional())
    .query(async ({ input }) => {
      const params = new URLSearchParams();
      if (input?.hours) params.set("hours", String(input.hours));
      const data = await apiFetch(`/metrics/overview?${params.toString()}`);
      return MetricsOverview.parse(data);
    }),
});
