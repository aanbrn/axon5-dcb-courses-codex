import { CircleAlertIcon } from "lucide-react";
import { useCallback, useLayoutEffect, useRef, useState } from "react";
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
  const labelMeasure = useRef<HTMLSpanElement>(null);
  const [labelClipped, setLabelClipped] = useState(false);
  const selectedLabel = ready
    ? state.roles.find(({ id }) => id === state.selectedId)?.label
    : undefined;
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

  useLayoutEffect(() => {
    const control = selector.current;
    const measure = labelMeasure.current;
    if (!control || !measure) return;

    const updateClipping = () => {
      const style = getComputedStyle(control);
      const valueWidth = control.clientWidth
        - parseFloat(style.paddingInlineStart)
        - parseFloat(style.paddingInlineEnd);
      setLabelClipped(measure.getBoundingClientRect().width > valueWidth);
    };

    updateClipping();
    // The measured text also resizes when the local font finishes loading.
    const observer = new ResizeObserver(updateClipping);
    observer.observe(control);
    observer.observe(measure);
    return () => observer.disconnect();
  }, [selectedLabel]);

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <header className="site-header">
        <div className="site-header__inner">
          <a className="site-home" href="/">
            DCB Courses
          </a>
          <nav className="site-nav" aria-label="Documentation">
            <a href={docsBase.href}>Documentation</a>
            <a href={quickStart}>Quick start</a>
          </nav>
          <div className="role-group">
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
            {selectedLabel !== undefined && (
              <>
                <div className="role-value-measure" aria-hidden="true">
                  <span ref={labelMeasure}>{selectedLabel}</span>
                </div>
                {labelClipped && (
                  <p className="role-full-name" aria-hidden="true">
                    {selectedLabel}
                  </p>
                )}
              </>
            )}
            <p className="role-status" role="status">{statusMessage}</p>
            {ready && state.roles.length === 1 && (
              <div className="role-notice">
                <h2>No demo students available</h2>
                <p>
                  You can continue as Administrator or read the <a href={quickStart}>quick start</a>.
                </p>
              </div>
            )}
            {(failed || retrying) && (
              <div className="role-recovery">
                {failed && (
                  <Alert variant="destructive">
                    <CircleAlertIcon aria-hidden="true" />
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
        </div>
      </header>
      <main className="home-main" id="main" tabIndex={-1}>
        <div className="home-content">
          <h1>Axon 5 DCB Courses</h1>
          <p>Explore how Axon 5 uses Dynamic Consistency Boundaries to enforce course enrollment rules.</p>
          <Button asChild>
            <a href={new URL("feasibility/phase-01/", docsBase).href}>Read feasibility report</a>
          </Button>
        </div>
      </main>
    </>
  );
}
