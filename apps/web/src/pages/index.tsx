import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ fontSize: 24, fontWeight: 600 }}>CoreQueue</h1>
      <ul style={{ marginTop: 16, display: "flex", gap: 16 }}>
        <li>
          <Link href="/dashboard">Dashboard</Link>
        </li>
        <li>
          <Link href="/jobs">Jobs</Link>
        </li>
        <li>
          <Link href="/submit">Submit</Link>
        </li>
        <li>
          <Link href="/runners">Runners</Link>
        </li>
        <li>
          <Link href="/policies">Policies</Link>
        </li>
      </ul>
    </main>
  );
}
