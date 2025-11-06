import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listPolicies, applyPolicy } from "src/api/policies";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";
import styles from "./policies.module.css";

export default function PoliciesPage() {
  const qc = useQueryClient();
  const listQ = useQuery({
    queryKey: ["policies"],
    queryFn: () => listPolicies(),
  });
  const [name, setName] = useState("team-policy");
  const [match, setMatch] = useState('{"team":"siml-tools"}');
  const [rules, setRules] = useState(
    '{"max_concurrent_gpu_jobs":2, "max_wall_time":"01:00:00"}',
  );
  const [dry, setDry] = useState<any>();
  const applyM = useMutation({
    mutationFn: async (dryRunOnly: boolean) =>
      applyPolicy(
        { name, match: JSON.parse(match), rules: JSON.parse(rules) },
        dryRunOnly,
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["policies"] }),
  });

  if (listQ.isLoading) return <Loading />;
  if (listQ.error) return <ErrorMessage text="Error loading policies" />;
  return (
    <PageContainer>
      <h1>Policies</h1>
      <section>
        <h2>Existing Policies</h2>
        <div className={styles.existingPoliciesContainer}>
          {listQ.data?.policies.length === 0 ? (
            <div className={styles.noPoliciesMessage}>
              No policies configured
            </div>
          ) : (
            <ul className={styles.policiesList}>
              {listQ.data?.policies.map((p) => (
                <li key={p.id} className={styles.policyItem}>
                  <div className={styles.policyHeader}>
                    {p.name}{" "}
                    <span className={styles.policyVersion}>v{p.version}</span>
                  </div>
                  <div className={styles.policyDetail}>
                    <strong>Match:</strong>{" "}
                    <code className={styles.policyCode}>
                      {JSON.stringify(p.match)}
                    </code>
                  </div>
                  <div className={styles.policyDetail}>
                    <strong>Rules:</strong>{" "}
                    <code className={styles.policyCode}>
                      {JSON.stringify(p.rules)}
                    </code>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
      <section className={styles.newPolicySection}>
        <h2>Apply New Policy</h2>
        <div className={styles.newPolicyContainer}>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>Policy Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., team-policy"
              className={styles.formInput}
            />
          </div>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>Match Criteria (JSON)</label>
            <textarea
              className={styles.formTextarea}
              value={match}
              onChange={(e) => setMatch(e.target.value)}
              placeholder='{"team": "example-team"}'
            />
          </div>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>Policy Rules (JSON)</label>
            <textarea
              className={styles.formTextareaLarge}
              value={rules}
              onChange={(e) => setRules(e.target.value)}
              placeholder='{"max_concurrent_gpu_jobs": 2, "max_wall_time": "01:00:00"}'
            />
          </div>
          <div className={styles.buttonGroup}>
            <button
              onClick={async () => {
                const r = await applyM.mutateAsync(true);
                setDry(r);
              }}
              className={styles.dryRunButton}
            >
              Dry Run
            </button>
            <button
              className="primary"
              onClick={() => applyM.mutate(false)}
              disabled={applyM.isPending}
            >
              {applyM.isPending ? "Applying..." : "Apply Policy"}
            </button>
          </div>
          {dry ? (
            <div className={styles.dryRunResult}>
              <h3 className={styles.dryRunTitle}>Dry Run Result</h3>
              <pre className={styles.dryRunPre}>
                {JSON.stringify(dry, null, 2)}
              </pre>
            </div>
          ) : null}
        </div>
      </section>
    </PageContainer>
  );
}
