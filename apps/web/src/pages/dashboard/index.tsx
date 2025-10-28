import { useQuery } from "@tanstack/react-query";
import { getOverview } from "src/api/metrics";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";
import { Card } from "src/components/Card/Card";
import styles from "./dashboard.module.css";

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
      <div className={styles.metricsGrid}>
        <Card title="CPU Avg" value={m.cpu_avg.toFixed(2)} />
        <Card title="GPU Avg" value={m.gpu_avg.toFixed(2)} />
        <Card title="Queue Avg (s)" value={m.queue_time_avg_sec.toFixed(1)} />
        <Card title="Run Avg (s)" value={m.run_time_avg_sec.toFixed(1)} />
      </div>
      <h2 className={styles.violationsTitle}>Policy Violations (Recent)</h2>
      <div className={styles.violationsContainer}>
        <div className={styles.violationRow}>
          <span className={styles.violationLabel}>
            Max wall-time violations
          </span>
          <span
            className={
              m.violations.max_wall_time > 0
                ? styles.violationValueError
                : styles.violationValueSuccess
            }
          >
            {m.violations.max_wall_time}
          </span>
        </div>
        <div className={styles.violationRow}>
          <span className={styles.violationLabel}>
            Thermal critical violations
          </span>
          <span
            className={
              m.violations.deny_if_device_thermal_state > 0
                ? styles.violationValueError
                : styles.violationValueSuccess
            }
          >
            {m.violations.deny_if_device_thermal_state}
          </span>
        </div>
        <div className={styles.violationRowLast}>
          <span className={styles.violationLabel}>Concurrency violations</span>
          <span
            className={
              m.violations.max_concurrent_gpu_jobs > 0
                ? styles.violationValueError
                : styles.violationValueSuccess
            }
          >
            {m.violations.max_concurrent_gpu_jobs}
          </span>
        </div>
      </div>
    </PageContainer>
  );
}
