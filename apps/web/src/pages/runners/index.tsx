import { useQuery } from "@tanstack/react-query";
import { listRunners } from "src/api/runners";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";
import { useState } from "react";
import styles from "./runners.module.css";

export default function RunnersPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["runners"],
    queryFn: () => listRunners(),
    refetchInterval: 5000,
  });
  const [page, setPage] = useState(1);
  const pageSize = 20;
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage text="Error loading runners" />;
  const items = data?.runners || [];
  const start = (page - 1) * pageSize;
  const pageItems = items.slice(start, start + pageSize);
  return (
    <PageContainer>
      <h1>Runners</h1>
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.tableHeader}>
              <th className={styles.tableHeaderCell}>Name</th>
              <th className={styles.tableHeaderCell}>Status</th>
              <th className={styles.tableHeaderCell}>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {pageItems.map((r, index) => (
              <tr
                key={r.id}
                className={
                  index < pageItems.length - 1
                    ? styles.tableRow
                    : styles.tableRowLast
                }
              >
                <td className={styles.tableCellName}>{r.name}</td>
                <td className={styles.tableCellDefault}>
                  <span
                    className={`${styles.statusBadge} ${
                      r.status === "ACTIVE"
                        ? styles.statusActive
                        : r.status === "INACTIVE"
                          ? styles.statusInactive
                          : styles.statusOther
                    }`}
                  >
                    {r.status}
                  </span>
                </td>
                <td className={styles.tableCellSecondary}>
                  {r.last_seen ?? "Never"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={styles.pagination}>
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          Previous
        </button>
        <span className={styles.pageInfo}>Page {page}</span>
        <button
          onClick={() =>
            setPage((p) => (p * pageSize < items.length ? p + 1 : p))
          }
          disabled={page * pageSize >= items.length}
        >
          Next
        </button>
      </div>
    </PageContainer>
  );
}
