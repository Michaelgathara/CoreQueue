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
        <h2>Existing</h2>
        <ul>
          {listQ.data?.policies.map((p) => (
            <li key={p.id}>
              {p.name} v{p.version} — match: {JSON.stringify(p.match)} rules:{" "}
              {JSON.stringify(p.rules)}
            </li>
          ))}
        </ul>
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Apply</h2>
        <div>
          <div>
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label>Match (JSON)</label>
            <textarea
              style={{ width: "100%", height: 120 }}
              value={match}
              onChange={(e) => setMatch(e.target.value)}
            />
          </div>
          <div>
            <label>Rules (JSON)</label>
            <textarea
              style={{ width: "100%", height: 160 }}
              value={rules}
              onChange={(e) => setRules(e.target.value)}
            />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={async () => {
                const r = await applyM.mutateAsync(true);
                setDry(r);
              }}
            >
              Dry Run
            </button>
            <button
              onClick={() => applyM.mutate(false)}
              disabled={applyM.isPending}
            >
              Apply
            </button>
          </div>
          {dry ? (
            <pre
              style={{
                background: "#111",
                color: "#eee",
                padding: 8,
                marginTop: 8,
              }}
            >
              {JSON.stringify(dry, null, 2)}
            </pre>
          ) : null}
        </div>
      </section>
    </PageContainer>
  );
}
