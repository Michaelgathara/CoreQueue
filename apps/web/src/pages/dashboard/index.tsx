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
      <h2 style={{ marginTop: 24 }}>Policy Violations (recent)</h2>
      <ul>
        <li>Max wall-time: {m.violations.max_wall_time}</li>
        <li>Thermal critical: {m.violations.deny_if_device_thermal_state}</li>
        <li>Concurrency (sim): {m.violations.max_concurrent_gpu_jobs}</li>
      </ul>
    </PageContainer>
  );
}
