import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cancelJob, fetchLogs, getJob, listArtifacts } from "src/api/jobs";
import styles from "./JobDetail.module.css";

export function JobDetail({ id }: { id: string }) {
  const qc = useQueryClient();
  const jobQ = useQuery({ queryKey: ["job", id], queryFn: () => getJob(id) });
  const artQ = useQuery({
    queryKey: ["job", id, "artifacts"],
    queryFn: () => listArtifacts(id),
  });
  const logsQ = useQuery({
    queryKey: ["job", id, "logs"],
    queryFn: () => fetchLogs(id, 8192),
    refetchInterval: 2000,
  });
  const cancelM = useMutation({
    mutationFn: () => cancelJob(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["job", id] }),
  });

  if (jobQ.isLoading) return <div className={styles.wrap}>Loading...</div>;
  if (jobQ.error) return <div className={styles.wrap}>Error loading job</div>;
  const j = jobQ.data!;
  return (
    <div className={styles.wrap}>
      <div>
        <h1>{j.name}</h1>
        <div>State: {j.state}</div>
        <div>
          Team: {j.team_id} Owner: {j.owner_id}
        </div>
        <div>
          Queued: {j.queued_at} Started: {j.started_at} Finished:{" "}
          {j.finished_at}
        </div>
        {j.state === "QUEUED" || j.state === "RUNNING" ? (
          <button
            className={styles.btn}
            onClick={() => cancelM.mutate()}
            disabled={cancelM.isPending}
          >
            Cancel
          </button>
        ) : null}
      </div>
      <section className={styles.section}>
        <h2>Logs</h2>
        <pre className={styles.log}>{logsQ.data ?? ""}</pre>
      </section>
      <section className={styles.section}>
        <h2>Artifacts</h2>
        <ul>
          {artQ.data?.artifacts.map((a) => (
            <li key={a}>
              <a
                href={`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/jobs/${id}/artifacts/${a}`}
                target="_blank"
                rel="noreferrer"
              >
                {a}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
