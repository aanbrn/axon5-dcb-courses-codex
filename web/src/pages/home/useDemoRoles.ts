import { useEffect, useState } from "react";
import { loadDemoRoles, type DemoRoleDirectory } from "../../shared/api/demoRoles";

const roleStorageKey = "courses.demo.role";

type DemoRole = DemoRoleDirectory["administrator"] | DemoRoleDirectory["students"][number];

type RoleState =
  | { status: "loading" }
  | { status: "failed" }
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
  const [state, setState] = useState<RoleState>({ status: "loading" });

  useEffect(() => {
    const request = new AbortController();
    loadDemoRoles(request.signal)
      .then(({ administrator, students }) => {
        if (request.signal.aborted) return;
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
        if (!request.signal.aborted) setState({ status: "failed" });
      });
    return () => request.abort();
  }, []);

  function selectRole(id: string) {
    if (state.status !== "ready" || !state.roles.some((role) => role.id === id)) return;
    storeRole(id);
    setState({ ...state, selectedId: id, fellBack: false });
  }

  return { state, selectRole };
}
