---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 11
total_count: 11
last_updated: 2026-11-25T16:26:24.012Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | deviation | bff/src/main/kotlin/courses/bff/BffApplication.kt |  | Documented existing public declarations and formatted the BFF build script. | fixed |  | 2026-11-25T13:53:55.917Z | 2026-11-25T13:54:21.858Z |
| 2 | 02 | deviation | docs-site/serve.mjs |  | Enforce the loopback boundary and keep configuration-specific preview addresses as text. | fixed |  | 2026-11-25T14:25:28.440Z | 2026-11-25T14:25:28.526Z |
| 3 | 02 | deviation | web/vite.config.ts |  | Initialize the Tailwind theme and Vite plugin in the tracer. | fixed |  | 2026-11-25T14:47:31.520Z | 2026-11-25T14:47:31.597Z |
| 4 | 02 | deviation | web/src/app/theme.css |  | Apply the focus outline immediately. | fixed |  | 2026-11-25T14:47:31.673Z | 2026-11-25T14:47:31.752Z |
| 5 | 02 | deviation | web/test/generated-client.test.ts |  | Disable dependency discovery for test-only Vite loaders. | fixed |  | 2026-11-25T14:47:31.828Z | 2026-11-25T14:47:31.909Z |
| 6 | 02 | deviation | web/src/pages/home/index.ts |  | Add the required authored FSD segments and public APIs. | fixed |  | 2026-11-25T15:09:51.334Z | 2026-11-25T15:10:02.483Z |
| 7 | 02 | deviation | web/package.json |  | Satisfy the Steiger toolchain peer in its own dependency graph. | fixed |  | 2026-11-25T15:10:02.551Z | 2026-11-25T15:10:02.620Z |
| 8 | 02 | deviation | web/vitest.config.ts |  | Allow the proof to read the installed dependency directory. | fixed |  | 2026-11-25T15:10:02.692Z | 2026-11-25T15:10:02.759Z |
| 9 | 02 | deviation | build.gradle.kts |  | Regenerated stale Gradle Kotlin DSL accessors. | fixed |  | 2026-11-25T15:36:00.432Z | 2026-11-25T15:36:00.506Z |
| 10 | 02 | deviation | tools/style/policy.json |  | Selected explicit Ruff lint rules. | fixed |  | 2026-11-25T15:36:00.575Z | 2026-11-25T15:36:00.649Z |
| 11 | 02 | deviation | build.gradle.kts |  | Preserve the installed pre-commit hook after clean build | fixed |  | 2026-11-25T16:26:02.804Z | 2026-11-25T16:26:24.012Z |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "02",
    "file": "bff/src/main/kotlin/courses/bff/BffApplication.kt",
    "line": null,
    "description": "Documented existing public declarations and formatted the BFF build script.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T13:53:55.917Z",
    "resolved_at": "2026-11-25T13:54:21.858Z",
    "milestone": "v1.0"
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "02",
    "file": "docs-site/serve.mjs",
    "line": null,
    "description": "Enforce the loopback boundary and keep configuration-specific preview addresses as text.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T14:25:28.440Z",
    "resolved_at": "2026-11-25T14:25:28.526Z",
    "milestone": "v1.0"
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "02",
    "file": "web/vite.config.ts",
    "line": null,
    "description": "Initialize the Tailwind theme and Vite plugin in the tracer.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T14:47:31.520Z",
    "resolved_at": "2026-11-25T14:47:31.597Z",
    "milestone": "v1.0"
  },
  {
    "id": 4,
    "kind": "deviation",
    "phase": "02",
    "file": "web/src/app/theme.css",
    "line": null,
    "description": "Apply the focus outline immediately.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T14:47:31.673Z",
    "resolved_at": "2026-11-25T14:47:31.752Z",
    "milestone": "v1.0"
  },
  {
    "id": 5,
    "kind": "deviation",
    "phase": "02",
    "file": "web/test/generated-client.test.ts",
    "line": null,
    "description": "Disable dependency discovery for test-only Vite loaders.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T14:47:31.828Z",
    "resolved_at": "2026-11-25T14:47:31.909Z",
    "milestone": "v1.0"
  },
  {
    "id": 6,
    "kind": "deviation",
    "phase": "02",
    "file": "web/src/pages/home/index.ts",
    "line": null,
    "description": "Add the required authored FSD segments and public APIs.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T15:09:51.334Z",
    "resolved_at": "2026-11-25T15:10:02.483Z",
    "milestone": "v1.0"
  },
  {
    "id": 7,
    "kind": "deviation",
    "phase": "02",
    "file": "web/package.json",
    "line": null,
    "description": "Satisfy the Steiger toolchain peer in its own dependency graph.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T15:10:02.551Z",
    "resolved_at": "2026-11-25T15:10:02.620Z",
    "milestone": "v1.0"
  },
  {
    "id": 8,
    "kind": "deviation",
    "phase": "02",
    "file": "web/vitest.config.ts",
    "line": null,
    "description": "Allow the proof to read the installed dependency directory.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T15:10:02.692Z",
    "resolved_at": "2026-11-25T15:10:02.759Z",
    "milestone": "v1.0"
  },
  {
    "id": 9,
    "kind": "deviation",
    "phase": "02",
    "file": "build.gradle.kts",
    "line": null,
    "description": "Regenerated stale Gradle Kotlin DSL accessors.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T15:36:00.432Z",
    "resolved_at": "2026-11-25T15:36:00.506Z",
    "milestone": "v1.0"
  },
  {
    "id": 10,
    "kind": "deviation",
    "phase": "02",
    "file": "tools/style/policy.json",
    "line": null,
    "description": "Selected explicit Ruff lint rules.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T15:36:00.575Z",
    "resolved_at": "2026-11-25T15:36:00.649Z",
    "milestone": "v1.0"
  },
  {
    "id": 11,
    "kind": "deviation",
    "phase": "02",
    "file": "build.gradle.kts",
    "line": null,
    "description": "Preserve the installed pre-commit hook after clean build",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-25T16:26:02.804Z",
    "resolved_at": "2026-11-25T16:26:24.012Z",
    "milestone": "v1.0"
  }
]
````
