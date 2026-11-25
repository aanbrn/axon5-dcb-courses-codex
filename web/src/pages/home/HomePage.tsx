import { useCallback, useLayoutEffect, useRef } from "react";
import { Alert, AlertDescription, Button, NativeSelect, NativeSelectOption } from "@/shared/ui";
import { useDemoRoles } from "./useDemoRoles";

const loadingMessage = "Loading demo roles…";
const fallbackMessage = "Your previous demo student is unavailable. You’re now using Administrator.";

export function HomePage({ docsBase }: { docsBase: URL }) {
  const { state, selectRole, retry } = useDemoRoles();
  const ready = state.status === "ready";
  const failed = state.status === "failed";
  const retrying = state.status === "retrying";
  const statusMessage = state.status === "loading" || retrying
    ? loadingMessage
    : ready && state.fellBack ? fallbackMessage : "";
  const quickStart = new URL("quick-start/", docsBase).href;
  const selector = useRef<HTMLSelectElement>(null);
  const restoreSelectorFocus = useRef(false);
  const trackRetryFocus = useCallback((button: HTMLButtonElement | null) => {
    if (!button) return;
    return () => {
      // Capture focus as the retry button leaves the DOM.
      restoreSelectorFocus.current = button.ownerDocument.activeElement === button;
    };
  }, []);

  useLayoutEffect(() => {
    if (ready && restoreSelectorFocus.current) {
      restoreSelectorFocus.current = false;
      selector.current?.focus();
    }
  }, [ready]);

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
          <NativeSelect
            id="demo-role"
            ref={selector}
            disabled={!ready}
            value={ready ? state.selectedId : ""}
            onChange={({ currentTarget }) => selectRole(currentTarget.value)}
          >
            {ready ? (
              state.roles.map(({ id, label }) => (
                <NativeSelectOption key={id} value={id}>
                  {label}
                </NativeSelectOption>
              ))
            ) : (
              <NativeSelectOption value="">
                {failed || retrying ? "Roles unavailable" : loadingMessage}
              </NativeSelectOption>
            )}
          </NativeSelect>
          <p role="status">{statusMessage}</p>
          {ready && state.roles.length === 1 && (
            <div>
              <h2>No demo students available</h2>
              <p>You can continue as Administrator or read the <a href={quickStart}>quick start</a>.</p>
            </div>
          )}
          {(failed || retrying) && (
            <div>
              {failed && (
                <Alert variant="destructive">
                  <AlertDescription>Could not load demo roles. Try again to switch roles.</AlertDescription>
                </Alert>
              )}
              <Button
                type="button"
                variant="outline"
                ref={trackRetryFocus}
                aria-disabled={retrying}
                onClick={retry}
              >
                Retry loading roles
              </Button>
            </div>
          )}
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        <h1>Axon 5 DCB Courses</h1>
        <p>Explore how Axon 5 uses Dynamic Consistency Boundaries to enforce course enrollment rules.</p>
        <Button asChild>
          <a href={new URL("feasibility/phase-01/", docsBase).href}>Read feasibility report</a>
        </Button>
      </main>
    </>
  );
}
