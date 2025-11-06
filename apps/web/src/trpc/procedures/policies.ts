import { initTRPC } from "@trpc/server";
import { z } from "zod";
import { apiFetch } from "../../lib/fetch";

const t = initTRPC.create();

export const PolicyOut = z.object({
  id: z.string(),
  name: z.string(),
  match: z.record(z.any()),
  rules: z.record(z.any()),
  version: z.number(),
});

export const PolicyIn = z.object({
  name: z.string(),
  match: z.record(z.any()),
  rules: z.record(z.any()),
});

export const policiesRouter = t.router({
  list: t.procedure.query(async () => {
    const data = await apiFetch(`/policies`);
    return z.object({ policies: z.array(PolicyOut) }).parse(data);
  }),
  apply: t.procedure
    .input(
      z.object({ policy: PolicyIn, dryRunOnly: z.boolean().default(false) }),
    )
    .mutation(async ({ input }) => {
      const params = new URLSearchParams();
      if (input.dryRunOnly) params.set("dry_run_only", "true");
      const data = await apiFetch(`/policies/apply?${params.toString()}`, {
        method: "POST",
        body: JSON.stringify(input.policy),
      });
      return data;
    }),
});
