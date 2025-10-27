import { useQuery } from "@tanstack/react-query";
import { listRunners } from "src/api/runners";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";
import { useState } from "react";

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
      <table style={{ width: "100%", marginTop: 12 }}>
        <thead>
          <tr>
            <th align="left">Name</th>
            <th align="left">Status</th>
            <th align="left">Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {pageItems.map((r) => (
            <tr key={r.id}>
              <td>{r.name}</td>
              <td>{r.status}</td>
              <td>{r.last_seen ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          Prev
        </button>
        <span>Page {page}</span>
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
