import Link from "next/link";

export default function Home() {
  return (
    <main
      style={{
        padding: "48px 24px",
        maxWidth: "1200px",
        margin: "0 auto",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div style={{ textAlign: "center", marginBottom: "48px" }}>
        <h1
          style={{
            fontSize: "48px",
            fontWeight: 700,
            marginBottom: "16px",
            color: "var(--text-primary)",
            letterSpacing: "-1px",
          }}
        >
          CoreQueue
        </h1>
        <p
          style={{
            fontSize: "18px",
            color: "var(--text-secondary)",
            maxWidth: "600px",
            lineHeight: "1.6",
          }}
        >
          High-performance job queue management system for distributed computing
          workloads
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 20,
          width: "100%",
          maxWidth: "800px",
        }}
      >
        <Link
          href="/dashboard"
          style={{
            display: "block",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "12px",
            padding: "24px",
            textDecoration: "none",
            transition: "all 0.2s ease",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              marginBottom: "8px",
              color: "var(--text-primary)",
            }}
          >
            📊 Dashboard
          </div>
          <div
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
            }}
          >
            View system metrics and policy violations
          </div>
        </Link>

        <Link
          href="/jobs"
          style={{
            display: "block",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "12px",
            padding: "24px",
            textDecoration: "none",
            transition: "all 0.2s ease",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              marginBottom: "8px",
              color: "var(--text-primary)",
            }}
          >
            🔧 Jobs
          </div>
          <div
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
            }}
          >
            Browse and manage job queue
          </div>
        </Link>

        <Link
          href="/submit"
          style={{
            display: "block",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "12px",
            padding: "24px",
            textDecoration: "none",
            transition: "all 0.2s ease",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              marginBottom: "8px",
              color: "var(--text-primary)",
            }}
          >
            ➕ Submit
          </div>
          <div
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
            }}
          >
            Submit new jobs to the queue
          </div>
        </Link>

        <Link
          href="/runners"
          style={{
            display: "block",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "12px",
            padding: "24px",
            textDecoration: "none",
            transition: "all 0.2s ease",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              marginBottom: "8px",
              color: "var(--text-primary)",
            }}
          >
            🏃 Runners
          </div>
          <div
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
            }}
          >
            Monitor runner status and health
          </div>
        </Link>

        <Link
          href="/policies"
          style={{
            display: "block",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "12px",
            padding: "24px",
            textDecoration: "none",
            transition: "all 0.2s ease",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              marginBottom: "8px",
              color: "var(--text-primary)",
            }}
          >
            📋 Policies
          </div>
          <div
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
            }}
          >
            Configure job execution policies
          </div>
        </Link>
      </div>
    </main>
  );
}
