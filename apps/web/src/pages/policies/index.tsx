import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listPolicies, applyPolicy } from "src/api/policies";
import { PageContainer } from "src/components/Layout/PageContainer";
import { Loading } from "src/components/Common/Loading";
import { ErrorMessage } from "src/components/Common/ErrorMessage";

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
        <div
          style={{
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          {listQ.data?.policies.length === 0 ? (
            <div
              style={{
                padding: "24px",
                textAlign: "center",
                color: "var(--text-tertiary)",
              }}
            >
              No policies configured
            </div>
          ) : (
            <ul style={{ margin: 0 }}>
              {listQ.data?.policies.map((p) => (
                <li
                  key={p.id}
                  style={{
                    padding: "16px 20px",
                    borderBottom: "1px solid var(--border-primary)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  }}
                >
                  <div
                    style={{
                      fontWeight: 600,
                      color: "var(--text-primary)",
                      fontSize: "16px",
                    }}
                  >
                    {p.name}{" "}
                    <span
                      style={{
                        color: "var(--text-tertiary)",
                        fontSize: "14px",
                        fontWeight: 400,
                      }}
                    >
                      v{p.version}
                    </span>
                  </div>
                  <div
                    style={{ fontSize: "14px", color: "var(--text-secondary)" }}
                  >
                    <strong>Match:</strong>{" "}
                    <code
                      style={{
                        background: "var(--bg-tertiary)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        fontSize: "12px",
                      }}
                    >
                      {JSON.stringify(p.match)}
                    </code>
                  </div>
                  <div
                    style={{ fontSize: "14px", color: "var(--text-secondary)" }}
                  >
                    <strong>Rules:</strong>{" "}
                    <code
                      style={{
                        background: "var(--bg-tertiary)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        fontSize: "12px",
                      }}
                    >
                      {JSON.stringify(p.rules)}
                    </code>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
      <section style={{ marginTop: 32 }}>
        <h2>Apply New Policy</h2>
        <div
          style={{
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "8px",
            padding: "24px",
            display: "grid",
            gap: "20px",
            maxWidth: "800px",
          }}
        >
          <div style={{ display: "grid", gap: "8px" }}>
            <label
              style={{
                color: "var(--text-secondary)",
                fontWeight: 500,
                fontSize: "14px",
              }}
            >
              Policy Name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., team-policy"
              style={{ width: "100%" }}
            />
          </div>
          <div style={{ display: "grid", gap: "8px" }}>
            <label
              style={{
                color: "var(--text-secondary)",
                fontWeight: 500,
                fontSize: "14px",
              }}
            >
              Match Criteria (JSON)
            </label>
            <textarea
              style={{
                width: "100%",
                height: 120,
                fontFamily:
                  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                fontSize: "13px",
              }}
              value={match}
              onChange={(e) => setMatch(e.target.value)}
              placeholder='{"team": "example-team"}'
            />
          </div>
          <div style={{ display: "grid", gap: "8px" }}>
            <label
              style={{
                color: "var(--text-secondary)",
                fontWeight: 500,
                fontSize: "14px",
              }}
            >
              Policy Rules (JSON)
            </label>
            <textarea
              style={{
                width: "100%",
                height: 160,
                fontFamily:
                  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                fontSize: "13px",
              }}
              value={rules}
              onChange={(e) => setRules(e.target.value)}
              placeholder='{"max_concurrent_gpu_jobs": 2, "max_wall_time": "01:00:00"}'
            />
          </div>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <button
              onClick={async () => {
                const r = await applyM.mutateAsync(true);
                setDry(r);
              }}
              style={{
                background: "var(--warning)",
                borderColor: "var(--warning)",
                color: "white",
              }}
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
            <div style={{ marginTop: "8px" }}>
              <h3
                style={{
                  fontSize: "14px",
                  color: "var(--text-secondary)",
                  marginBottom: "8px",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                Dry Run Result
              </h3>
              <pre
                style={{
                  background: "var(--bg-tertiary)",
                  color: "var(--text-primary)",
                  padding: "16px",
                  borderRadius: "6px",
                  border: "1px solid var(--border-primary)",
                  fontSize: "12px",
                  lineHeight: "1.5",
                  overflow: "auto",
                }}
              >
                {JSON.stringify(dry, null, 2)}
              </pre>
            </div>
          ) : null}
        </div>
      </section>
    </PageContainer>
  );
}
