import styles from "./ErrorMessage.module.css";

export function ErrorMessage({
  text = "Something went wrong.",
}: {
  text?: string;
}) {
  return <div className={styles.wrap}>{text}</div>;
}
