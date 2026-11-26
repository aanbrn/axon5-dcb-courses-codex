import { listDemoRoles } from "../../../build/generated/client";

export async function loadDemoRoles(signal?: AbortSignal) {
  const response = await listDemoRoles({ signal, redirect: "error" });
  if (response.status !== 200) {
    throw new Error(`Could not load demo roles: HTTP ${response.status}`);
  }
  const contentType = response.headers
    .get("content-type")
    ?.split(";")[0]
    ?.trim()
    .toLowerCase();
  if (contentType !== "application/json") {
    throw new Error("The demo role directory must be JSON.");
  }

  const directory = response.data;
  const ids = [
    directory.administrator.id,
    ...directory.students.map(({ id }) => id),
  ];
  if (new Set(ids).size !== ids.length) {
    throw new Error("The demo role directory has duplicate identifiers.");
  }

  return directory;
}

export type DemoRoleDirectory = Awaited<ReturnType<typeof loadDemoRoles>>;
