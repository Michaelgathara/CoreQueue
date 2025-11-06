import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitJob } from "src/api/jobs";
import styles from "./SubmitForm.module.css";

export function SubmitForm() {
  const [mode, setMode] = useState<"yaml" | "json" | "form">("form");
  const [yaml, setYaml] = useState("");
  const [json, setJson] = useState("");
  const [name, setName] = useState("demo");
  const [owner, setOwner] = useState("Michael");
  const [team, setTeam] = useState("siml-tools");
  const [priority, setPriority] = useState("normal");
  const [entrypoint, setEntrypoint] = useState("echo hi");

  const submitM = useMutation({
    mutationFn: async () => {
      if (mode === "yaml") return submitJob({ yaml });
      if (mode === "json") {
        try {
          const spec = JSON.parse(json);
          return submitJob({ spec });
        } catch {
          throw new Error("Invalid JSON");
        }
      }
      const spec = {
        name,
        owner,
        team,
        priority,
        runtime: { kind: "local", entrypoint },
      } as const;
      return submitJob({ spec });
    },
  });

  return (
    <div className={styles.wrap}>
      <div className={styles.row}>
        <div className={styles.radio}>
          <label>
            <input
              type="radio"
              checked={mode === "form"}
              onChange={() => setMode("form")}
            />{" "}
            Form
          </label>
          <label>
            <input
              type="radio"
              checked={mode === "json"}
              onChange={() => setMode("json")}
            />{" "}
            JSON
          </label>
          <label>
            <input
              type="radio"
              checked={mode === "yaml"}
              onChange={() => setMode("yaml")}
            />{" "}
            YAML
          </label>
        </div>
        <button
          className={styles.btn}
          disabled={submitM.isPending}
          onClick={() => submitM.mutate()}
        >
          Submit
        </button>
      </div>
      {mode === "form" ? (
        <div className={styles.grid}>
          <div className={styles.field}>
            <label className={styles.label}>Name</label>
            <input
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Owner</label>
            <input
              className={styles.input}
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Team</label>
            <input
              className={styles.input}
              value={team}
              onChange={(e) => setTeam(e.target.value)}
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Priority</label>
            <select
              className={styles.select}
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            >
              <option value="low">low</option>
              <option value="normal">normal</option>
              <option value="high">high</option>
            </select>
          </div>
          <div className={styles.field} style={{ gridColumn: "1 / span 2" }}>
            <label className={styles.label}>Entrypoint</label>
            <input
              className={styles.input}
              value={entrypoint}
              onChange={(e) => setEntrypoint(e.target.value)}
            />
            <div className={styles.hint}>
              Shell command run by the runner (e.g., echo hi)
            </div>
          </div>
        </div>
      ) : mode === "json" ? (
        <textarea
          className={styles.textarea}
          value={json}
          onChange={(e) => setJson(e.target.value)}
          placeholder='{"name":"demo","owner":"mike","team":"siml-tools","runtime":{"kind":"local","entrypoint":"echo hi"}}'
        />
      ) : (
        <textarea
          className={styles.textarea}
          value={yaml}
          onChange={(e) => setYaml(e.target.value)}
          placeholder={
            "name: demo\nowner: mike\nteam: siml-tools\nruntime:\n  kind: local\n  entrypoint: echo hi"
          }
        />
      )}
      {submitM.error ? (
        <div className={styles.statusErr}>Error submitting job</div>
      ) : null}
      {submitM.data ? (
        <div className={styles.statusOk}>Submitted: {submitM.data.id}</div>
      ) : null}
    </div>
  );
}
