import { useQuery } from "@tanstack/react-query";
import { getOverview } from "src/api/metrics";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";
import { Card } from "src/components/Card/Card";

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics-overview"],
    queryFn: () => getOverview(1),
    refetchInterval: 5000,
  });
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage text="Error loading metrics" />;
  const m = data!;
  return (
    <PageContainer>
      <h1>Dashboard</h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          marginTop: 12,
        }}
      >
        <Card title="CPU Avg" value={m.cpu_avg.toFixed(2)} />
        <Card title="GPU Avg" value={m.gpu_avg.toFixed(2)} />
        <Card title="Queue Avg (s)" value={m.queue_time_avg_sec.toFixed(1)} />
        <Card title="Run Avg (s)" value={m.run_time_avg_sec.toFixed(1)} />
      </div>
      <h2 style={{ marginTop: 32 }}>Policy Violations (Recent)</h2>
      <div
        style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-primary)",
          borderRadius: "8px",
          padding: "20px",
          display: "grid",
          gap: "12px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "8px 0",
            borderBottom: "1px solid var(--border-primary)",
          }}
        >
          <span style={{ color: "var(--text-secondary)" }}>
            Max wall-time violations
          </span>
          <span
            style={{
              color:
                m.violations.max_wall_time > 0
                  ? "var(--error)"
                  : "var(--success)",
              fontWeight: 600,
              fontSize: "16px",
            }}
          >
            {m.violations.max_wall_time}
          </span>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "8px 0",
            borderBottom: "1px solid var(--border-primary)",
          }}
        >
          <span style={{ color: "var(--text-secondary)" }}>
            Thermal critical violations
          </span>
          <span
            style={{
              color:
                m.violations.deny_if_device_thermal_state > 0
                  ? "var(--error)"
                  : "var(--success)",
              fontWeight: 600,
              fontSize: "16px",
            }}
          >
            {m.violations.deny_if_device_thermal_state}
          </span>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "8px 0",
          }}
        >
          <span style={{ color: "var(--text-secondary)" }}>
            Concurrency violations
          </span>
          <span
            style={{
              color:
                m.violations.max_concurrent_gpu_jobs > 0
                  ? "var(--error)"
                  : "var(--success)",
              fontWeight: 600,
              fontSize: "16px",
            }}
          >
            {m.violations.max_concurrent_gpu_jobs}
          </span>
        </div>
      </div>
    </PageContainer>
  );
}
