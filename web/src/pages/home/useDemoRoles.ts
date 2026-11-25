import { useCallback, useEffect, useRef, useState } from "react";
import { loadDemoRoles, type DemoRoleDirectory } from "../../shared/api/demoRoles";

const roleStorageKey = "courses.demo.role";

type DemoRole = DemoRoleDirectory["administrator"] | DemoRoleDirectory["students"][number];

type RoleState =
  | { status: "initial" | "loading" | "failed" | "retrying" }
  | {
      status: "ready";
      roles: DemoRole[];
      selectedId: string;
      fellBack: boolean;
    };

function readStoredRole() {
  try {
    return window.sessionStorage.getItem(roleStorageKey);
  } catch {
    return null;
  }
}

function storeRole(id: string) {
  try {
    window.sessionStorage.setItem(roleStorageKey, id);
  } catch {
    // Keep the active selection in React state when tab storage is unavailable.
  }
}

export function useDemoRoles() {
  const [state, setState] = useState<RoleState>({ status: "initial" });
  const activeRequest = useRef<AbortController | null>(null);

  const requestDirectory = useCallback((status: "loading" | "retrying") => {
    if (activeRequest.current) return;
    const request = new AbortController();
    activeRequest.current = request;
    setState({ status });

    loadDemoRoles(request.signal)
      .then(({ administrator, students }) => {
        if (activeRequest.current !== request) return;
        const roles = [administrator, ...students];
        const saved = readStoredRole();
        const restored = roles.find(({ id }) => id === saved);
        const fellBack = saved !== null && restored === undefined;
        if (fellBack) storeRole(administrator.id);
        setState({
          status: "ready",
          roles,
          selectedId: restored?.id ?? administrator.id,
          fellBack,
        });
      })
      .catch(() => {
        if (activeRequest.current === request) setState({ status: "failed" });
      })
      .finally(() => {
        if (activeRequest.current === request) activeRequest.current = null;
      });
  }, []);

  useEffect(() => {
    requestDirectory("loading");
    return () => {
      activeRequest.current?.abort();
      activeRequest.current = null;
    };
  }, [requestDirectory]);

  function retry() {
    if (state.status === "failed") requestDirectory("retrying");
  }

  function selectRole(id: string) {
    if (state.status !== "ready" || !state.roles.some((role) => role.id === id)) return;
    storeRole(id);
    setState({ ...state, selectedId: id, fellBack: false });
  }

  return { state, selectRole, retry };
}
