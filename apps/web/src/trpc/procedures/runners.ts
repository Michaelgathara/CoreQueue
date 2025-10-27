import { initTRPC } from "@trpc/server";
import { z } from "zod";
import { apiFetch } from "../../lib/fetch";

const t = initTRPC.create();

export const Runner = z.object({
  id: z.string(),
  name: z.string(),
  status: z.string(),
  last_seen: z.string().nullable(),
});

export const runnersRouter = t.router({
  list: t.procedure.query(async () => {
    const data = await apiFetch(`/runners`);
    return z.object({ runners: z.array(Runner) }).parse(data);
  }),
});
