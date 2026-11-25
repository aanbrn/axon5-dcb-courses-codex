import { useDemoRoles } from "./useDemoRoles";

const loadingMessage = "Loading demo roles…";
const fallbackMessage = "Your previous demo student is unavailable. You’re now using Administrator.";

export function HomePage({ docsBase }: { docsBase: URL }) {
  const { state, selectRole } = useDemoRoles();
  const ready = state.status === "ready";
  const loading = state.status === "loading";
  const quickStart = new URL("quick-start/", docsBase).href;

  return (
    <>
      <a href="#main">Skip to main content</a>
      <header>
        <a href="/">DCB Courses</a>
        <nav aria-label="Documentation">
          <a href={docsBase.href}>Documentation</a>
          <a href={quickStart}>Quick start</a>
        </nav>
        <div>
          <label htmlFor="demo-role">Demo role</label>
          <select
            id="demo-role"
            disabled={!ready}
            value={ready ? state.selectedId : ""}
            onChange={({ currentTarget }) => selectRole(currentTarget.value)}
          >
            {ready ? (
              state.roles.map(({ id, label }) => (
                <option key={id} value={id}>
                  {label}
                </option>
              ))
            ) : (
              <option value="">{loading ? loadingMessage : "Roles unavailable"}</option>
            )}
          </select>
          <p role="status">
            {ready && state.fellBack ? fallbackMessage : ""}
          </p>
          {state.status === "failed" && <p role="alert">Could not load demo roles.</p>}
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
