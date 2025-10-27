import { apiFetch } from "../lib/fetch";
import { PolicyIn, PolicyOut, DryRunResult } from "../schemas/policy";
import { z } from "zod";

export async function listPolicies() {
  const data = await apiFetch(`/policies`);
  return z.object({ policies: z.array(PolicyOut) }).parse(data);
}

export async function applyPolicy(
  policy: z.infer<typeof PolicyIn>,
  dryRunOnly?: boolean,
) {
  const qs = new URLSearchParams();
  if (dryRunOnly) qs.set("dry_run_only", "true");
  const data = await apiFetch(`/policies/apply?${qs.toString()}`, {
    method: "POST",
    body: JSON.stringify(policy),
  });
  try {
    return DryRunResult.parse(data);
  } catch {
    return data as { id: string; version: number };
  }
}
