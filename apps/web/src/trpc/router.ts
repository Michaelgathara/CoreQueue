import { initTRPC } from "@trpc/server";
import { z } from "zod";
import superjson from "superjson";
import { jobsRouter } from "./procedures/jobs";
import { runnersRouter } from "./procedures/runners";
import { metricsRouter } from "./procedures/metrics";
import { policiesRouter } from "./procedures/policies";

const t = initTRPC.context<{}>().create({ transformer: superjson });

export const appRouter = t.router({
  jobs: jobsRouter,
  runners: runnersRouter,
  metrics: metricsRouter,
  policies: policiesRouter,
});

export type AppRouter = typeof appRouter;
