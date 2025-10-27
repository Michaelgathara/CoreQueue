import { apiFetch } from "../lib/fetch";
import { Runner } from "../schemas/runner";
import { z } from "zod";

export async function listRunners() {
  const data = await apiFetch(`/runners`);
  return z.object({ runners: z.array(Runner) }).parse(data);
}
