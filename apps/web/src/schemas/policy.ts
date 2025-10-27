import { z } from "zod";

export const PolicyOut = z.object({
  id: z.string(),
  name: z.string(),
  match: z.record(z.string(), z.any()),
  rules: z.record(z.string(), z.any()),
  version: z.coerce.number(),
});

export const PolicyIn = z.object({
  name: z.string(),
  match: z.record(z.string(), z.any()),
  rules: z.record(z.string(), z.any()),
});

export const DryRunResult = z.object({
  evaluated: z.number().optional(),
  would_allow: z.number(),
  would_deny: z.number(),
  violations_by_rule: z.record(z.number(), z.any()).optional(),
  examples: z
    .array(z.object({ job_id: z.string(), reason: z.string() }))
    .optional(),
});

export type Policy = z.infer<typeof PolicyOut>;
export type DryRun = z.infer<typeof DryRunResult>;
