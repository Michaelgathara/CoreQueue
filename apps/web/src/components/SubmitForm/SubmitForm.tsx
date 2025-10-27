import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitJob } from "src/api/jobs";
import styles from "./SubmitForm.module.css";

export function SubmitForm() {
  const [mode, setMode] = useState<"yaml" | "json">("json");
  const [yaml, setYaml] = useState("");
  const [json, setJson] = useState("");

  const submitM = useMutation({
    mutationFn: async () => {
      if (mode === "yaml") return submitJob({ yaml });
      try {
        const spec = JSON.parse(json);
        return submitJob({ spec });
      } catch {
        throw new Error("Invalid JSON");
      }
    },
  });

  return (
    <div className={styles.wrap}>
      <div className={styles.row}>
        <div className={styles.radio}>
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
      {mode === "json" ? (
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
