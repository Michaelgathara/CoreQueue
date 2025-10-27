import { z } from "zod";

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

export type Metrics = z.infer<typeof MetricsOverview>;
