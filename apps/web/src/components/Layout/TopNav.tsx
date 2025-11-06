import Link from "next/link";
import styles from "./TopNav.module.css";

export function TopNav() {
  return (
    <div className={styles.bar}>
      <div className={styles.title}>CoreQueue</div>
      <div className={styles.links}>
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/jobs">Jobs</Link>
        <Link href="/submit">Submit</Link>
        <Link href="/runners">Runners</Link>
        <Link href="/policies">Policies</Link>
      </div>
    </div>
  );
}
