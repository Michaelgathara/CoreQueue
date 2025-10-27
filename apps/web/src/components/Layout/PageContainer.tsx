import styles from "./PageContainer.module.css";
import { ReactNode } from "react";

export function PageContainer({ children }: { children: ReactNode }) {
  return <div className={styles.container}>{children}</div>;
}
