import Link from "next/link";
import styles from "./home.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <h1 className={styles.title}>CoreQueue</h1>
        <p className={styles.description}>
          High-performance job queue management system for distributed computing
          workloads
        </p>
      </div>

      <div className={styles.navigationGrid}>
        <Link href="/dashboard" className={styles.navigationCard}>
          <div className={styles.cardTitle}>📊 Dashboard</div>
          <div className={styles.cardDescription}>
            View system metrics and policy violations
          </div>
        </Link>

        <Link href="/jobs" className={styles.navigationCard}>
          <div className={styles.cardTitle}>🔧 Jobs</div>
          <div className={styles.cardDescription}>
            Browse and manage job queue
          </div>
        </Link>

        <Link href="/submit" className={styles.navigationCard}>
          <div className={styles.cardTitle}>➕ Submit</div>
          <div className={styles.cardDescription}>
            Submit new jobs to the queue
          </div>
        </Link>

        <Link href="/runners" className={styles.navigationCard}>
          <div className={styles.cardTitle}>🏃 Runners</div>
          <div className={styles.cardDescription}>
            Monitor runner status and health
          </div>
        </Link>

        <Link href="/policies" className={styles.navigationCard}>
          <div className={styles.cardTitle}>📋 Policies</div>
          <div className={styles.cardDescription}>
            Configure job execution policies
          </div>
        </Link>
      </div>
    </main>
  );
}
