import { z } from "zod";

export const Runner = z.object({
  id: z.string(),
  name: z.string(),
  status: z.string(),
  last_seen: z.string().nullable(),
});

export type RunnerT = z.infer<typeof Runner>;
