import { apiFetch } from "../lib/fetch";
import { JobListOut, JobOut } from "../schemas/job";

export async function listJobs(params?: {
  state?: string;
  team?: string;
  owner?: string;
  page?: number;
  limit?: number;
}) {
  const qs = new URLSearchParams();
  if (params?.state) qs.set("state", params.state);
  if (params?.team) qs.set("team", params.team);
  if (params?.owner) qs.set("owner", params.owner);
  if (params?.page) qs.set("page", String(params.page));
  if (params?.limit) qs.set("limit", String(params.limit));
  const data = await apiFetch(`/jobs?${qs.toString()}`);
  return JobListOut.parse(data);
}

export async function getJob(id: string) {
  const data = await apiFetch(`/jobs/${id}`);
  return JobOut.parse(data);
}

export async function submitJob(body: { yaml?: string; spec?: unknown }) {
  const data = await apiFetch(`/jobs/submit`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  return JobOut.parse(data);
}

export async function cancelJob(id: string) {
  const data = await apiFetch(`/jobs/${id}/cancel`, { method: "POST" });
  return JobOut.parse(data);
}

export async function listArtifacts(id: string) {
  return apiFetch<{ artifacts: string[] }>(`/jobs/${id}/artifacts`);
}

export async function fetchLogs(id: string, maxBytes?: number) {
  const qs = new URLSearchParams();
  if (maxBytes) qs.set("max_bytes", String(maxBytes));
  return apiFetch<string>(`/jobs/${id}/logs?${qs.toString()}`);
}
