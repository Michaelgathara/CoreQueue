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
      <div
        style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-primary)",
          borderRadius: "8px",
          overflow: "hidden",
          marginTop: 20,
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "var(--bg-tertiary)" }}>
              <th
                style={{
                  padding: "16px 12px",
                  textAlign: "left",
                  color: "var(--text-secondary)",
                  fontWeight: 600,
                  fontSize: "12px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  borderBottom: "1px solid var(--border-primary)",
                }}
              >
                Name
              </th>
              <th
                style={{
                  padding: "16px 12px",
                  textAlign: "left",
                  color: "var(--text-secondary)",
                  fontWeight: 600,
                  fontSize: "12px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  borderBottom: "1px solid var(--border-primary)",
                }}
              >
                Status
              </th>
              <th
                style={{
                  padding: "16px 12px",
                  textAlign: "left",
                  color: "var(--text-secondary)",
                  fontWeight: 600,
                  fontSize: "12px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  borderBottom: "1px solid var(--border-primary)",
                }}
              >
                Last Seen
              </th>
            </tr>
          </thead>
          <tbody>
            {pageItems.map((r, index) => (
              <tr
                key={r.id}
                style={{
                  borderBottom:
                    index < pageItems.length - 1
                      ? "1px solid var(--border-primary)"
                      : "none",
                }}
              >
                <td
                  style={{
                    padding: "12px",
                    color: "var(--text-primary)",
                    fontWeight: 500,
                  }}
                >
                  {r.name}
                </td>
                <td style={{ padding: "12px" }}>
                  <span
                    style={{
                      padding: "4px 8px",
                      borderRadius: "4px",
                      fontSize: "12px",
                      fontWeight: 500,
                      textTransform: "uppercase",
                      background:
                        r.status === "ACTIVE"
                          ? "var(--success-bg)"
                          : r.status === "INACTIVE"
                            ? "var(--error-bg)"
                            : "var(--warning-bg)",
                      color:
                        r.status === "ACTIVE"
                          ? "var(--success)"
                          : r.status === "INACTIVE"
                            ? "var(--error)"
                            : "var(--warning)",
                    }}
                  >
                    {r.status}
                  </span>
                </td>
                <td
                  style={{
                    padding: "12px",
                    color: "var(--text-secondary)",
                    fontSize: "14px",
                  }}
                >
                  {r.last_seen ?? "Never"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          justifyContent: "center",
          marginTop: 20,
          padding: 16,
        }}
      >
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          Previous
        </button>
        <span
          style={{
            color: "var(--text-secondary)",
            fontWeight: 500,
          }}
        >
          Page {page}
        </span>
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
