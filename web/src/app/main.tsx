import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { loadDemoRoles, type DemoRoleDirectory } from "../shared/api/demoRoles";

const docsBase = new URL(
  import.meta.env.VITE_DOCS_BASE || "http://127.0.0.1:8081/",
  window.location.origin,
);
if (!docsBase.pathname.endsWith("/")) docsBase.pathname += "/";

function App() {
  const [directory, setDirectory] = useState<DemoRoleDirectory>();
  const [selectedRole, setSelectedRole] = useState("");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const request = new AbortController();
    loadDemoRoles(request.signal)
      .then((loaded) => {
        setDirectory(loaded);
        setSelectedRole(loaded.administrator.id);
      })
      .catch(() => {
        if (!request.signal.aborted) setFailed(true);
      });
    return () => request.abort();
  }, []);

  return (
    <>
      <a href="#main">Skip to main content</a>
      <header>
        <a href="/">DCB Courses</a>
        <nav aria-label="Documentation">
          <a href={docsBase.href}>Documentation</a>
          <a href={new URL("quick-start/", docsBase).href}>Quick start</a>
        </nav>
        <div>
          <label htmlFor="demo-role">Demo role</label>
          <select
            id="demo-role"
            disabled={!directory}
            value={selectedRole}
            onChange={({ currentTarget }) => setSelectedRole(currentTarget.value)}
          >
            {directory ? (
              [directory.administrator, ...directory.students].map(({ id, label }) => (
                <option key={id} value={id}>
                  {label}
                </option>
              ))
            ) : (
              <option value="">{failed ? "Roles unavailable" : "Loading demo roles…"}</option>
            )}
          </select>
          {failed && <p role="alert">Could not load demo roles.</p>}
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        <h1>Axon 5 DCB Courses</h1>
        <p>Explore how Axon 5 uses Dynamic Consistency Boundaries to enforce course enrollment rules.</p>
        <a href={new URL("feasibility/phase-01/", docsBase).href}>Read feasibility report</a>
      </main>
    </>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("The application mount point is missing.");
createRoot(root).render(<App />);
