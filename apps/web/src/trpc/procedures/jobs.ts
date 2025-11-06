import { initTRPC } from "@trpc/server";
import { z } from "zod";
import { apiFetch } from "../../lib/fetch";

const t = initTRPC.create();

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

export const jobsRouter = t.router({
  list: t.procedure
    .input(
      z
        .object({
          state: z.string().optional(),
          team: z.string().optional(),
          owner: z.string().optional(),
          page: z.number().optional(),
          limit: z.number().optional(),
        })
        .optional(),
    )
    .query(async ({ input }) => {
      const params = new URLSearchParams();
      if (input?.state) params.set("state", input.state);
      if (input?.team) params.set("team", input.team);
      if (input?.owner) params.set("owner", input.owner);
      if (input?.page) params.set("page", String(input.page));
      if (input?.limit) params.set("limit", String(input.limit));
      const data = await apiFetch(`/jobs?${params.toString()}`);
      return JobListOut.parse(data);
    }),

  get: t.procedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      const data = await apiFetch(`/jobs/${input.id}`);
      return JobOut.parse(data);
    }),

  submit: t.procedure
    .input(z.object({ yaml: z.string().optional(), spec: z.any().optional() }))
    .mutation(async ({ input }) => {
      const data = await apiFetch(`/jobs/submit`, {
        method: "POST",
        body: JSON.stringify(input),
      });
      return JobOut.parse(data);
    }),

  cancel: t.procedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      const data = await apiFetch(`/jobs/${input.id}/cancel`, {
        method: "POST",
      });
      return JobOut.parse(data);
    }),

  artifacts: t.procedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      const data = await apiFetch(`/jobs/${input.id}/artifacts`);
      return z.object({ artifacts: z.array(z.string()) }).parse(data);
    }),

  logs: t.procedure
    .input(z.object({ id: z.string(), maxBytes: z.number().optional() }))
    .query(async ({ input }) => {
      const params = new URLSearchParams();
      if (input.maxBytes) params.set("max_bytes", String(input.maxBytes));
      const data = await apiFetch<string>(
        `/jobs/${input.id}/logs?${params.toString()}`,
      );
      return data;
    }),
});
