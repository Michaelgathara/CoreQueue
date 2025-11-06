import styles from "./Loading.module.css";

export function Loading({ text = "Loading..." }: { text?: string }) {
  return <div className={styles.wrap}>{text}</div>;
}
