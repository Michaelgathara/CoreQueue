import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import { listJobs } from "src/api/jobs";
import styles from "./JobTable.module.css";

export function JobTable() {
  const [state, setState] = useState<string>("");
  const [team, setTeam] = useState<string>("");
  const [owner, setOwner] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const limit = 20;
  const { data, isLoading, error } = useQuery({
    queryKey: ["jobs", { state, team, owner, page, limit }],
    queryFn: () =>
      listJobs({
        state: state || undefined,
        team: team || undefined,
        owner: owner || undefined,
        page,
        limit,
      }),
  });
  return (
    <div className={styles.wrap}>
      <div className={styles.filters}>
        <select
          className={styles.control}
          value={state}
          onChange={(e) => {
            setPage(1);
            setState(e.target.value);
          }}
        >
          <option value="">All</option>
          <option value="QUEUED">QUEUED</option>
          <option value="CLAIMED">CLAIMED</option>
          <option value="RUNNING">RUNNING</option>
          <option value="SUCCEEDED">SUCCEEDED</option>
          <option value="FAILED">FAILED</option>
          <option value="CANCELLED">CANCELLED</option>
        </select>
        <input
          className={styles.control}
          placeholder="Team"
          value={team}
          onChange={(e) => {
            setPage(1);
            setTeam(e.target.value);
          }}
        />
        <input
          className={styles.control}
          placeholder="Owner"
          value={owner}
          onChange={(e) => {
            setPage(1);
            setOwner(e.target.value);
          }}
        />
      </div>
      {isLoading ? (
        <div>Loading...</div>
      ) : error ? (
        <div>Error</div>
      ) : (
        <>
          <table className={styles.table}>
            <thead>
              <tr>
                <th align="left">Name</th>
                <th align="left">State</th>
                <th align="left">Team</th>
                <th align="left">Owner</th>
                <th align="left">Queued</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((j) => (
                <tr key={j.id}>
                  <td>
                    <Link href={`/jobs/${j.id}`}>{j.name}</Link>
                  </td>
                  <td>{j.state}</td>
                  <td>{j.team_id}</td>
                  <td>{j.owner_id}</td>
                  <td>{j.queued_at ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={styles.pager}>
            <button
              className={styles.btn}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              Prev
            </button>
            <span>Page {page}</span>
            <button
              className={styles.btn}
              onClick={() =>
                setPage((p) => (data && p * limit < data.total ? p + 1 : p))
              }
              disabled={!data || page * limit >= data.total}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
