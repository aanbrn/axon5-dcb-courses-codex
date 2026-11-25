---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 1
total_count: 1
last_updated: 2026-11-25T13:54:21.858Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | deviation | bff/src/main/kotlin/courses/bff/BffApplication.kt |  | Documented existing public declarations and formatted the BFF build script. | fixed |  | 2026-11-25T13:53:55.917Z | 2026-11-25T13:54:21.858Z |

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
  }
]
````
