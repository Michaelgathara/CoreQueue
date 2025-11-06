import { z } from "zod";

export const JobOut = z.object({
  id: z.string(),
  name: z.string(),
  team_id: z.string(),
  owner_id: z.string(),
  priority: z.string(),
  state: z.string(),
  queued_at: z.string().nullable(),
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
});

export const JobListOut = z.object({
  items: z.array(JobOut),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
});

export type Job = z.infer<typeof JobOut>;
export type JobList = z.infer<typeof JobListOut>;
