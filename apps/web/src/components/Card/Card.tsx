import styles from "./Card.module.css";

export function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className={styles.card}>
      <div className={styles.title}>{title}</div>
      <div className={styles.value}>{value}</div>
    </div>
  );
}
