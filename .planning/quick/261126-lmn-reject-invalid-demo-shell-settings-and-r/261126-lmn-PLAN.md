---
phase: quick-261126-lmn
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - web/vite.config.ts
  - web/src/app/main.tsx
  - web/test/client-graph.py
  - bff/src/main/resources/static/openapi.json
  - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
  - web/test/generated-client.test.ts
  - bff/src/main/kotlin/courses/bff/BffApplication.kt
  - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
  - web/test/role-states.test.tsx
autonomous: true
requirements: [FND-06, CQRS-04, UI-03]
estimate:
  tokens: 21000
  raw_tokens: 21000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - An invalid effective VITE_DOCS_BASE stops the build and development startup with a diagnostic naming the setting. The documented local and hosted links resolve under their full prefix.
    - The published response schema rejects whitespace-only identifiers and labels for either role in the generated client and the independent HTTP contract suite.
    - The BFF constructs directories with case-sensitive, directory-wide unique IDs. A malformed reply leaves the reader with the existing alert, retry and documentation links.
  artifacts:
    - path: web/vite.config.ts
      provides: Documentation base resolution during Vite configuration
    - path: bff/src/main/resources/static/openapi.json
      provides: Published string constraints and the directory identity rule
    - path: bff/src/main/kotlin/courses/bff/BffApplication.kt
      provides: Construction-time protection for the directory served over HTTP
  key_links:
    - from: web/vite.config.ts
      to: web/src/app/main.tsx
      via: The normalized documentation base consumed by HomePage
    - from: bff/src/main/resources/static/openapi.json
      to: web/src/shared/api/demoRoles.ts
      via: Orval-generated Fetch and Zod response validation followed by the adapter's exact-ID check
---

<objective>
Close WR-01 and WR-02 from the Phase 02 application slice review. Catch a mistyped docs URL before the shell is served and make the published and implemented role-directory guarantees agree.
</objective>

<context>
@AGENTS.md
@.planning/STATE.md
@.planning/quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md
@.planning/phases/02-build-and-ui-foundations/02-CONTEXT.md
@docs/maintainer-guide.md
@web/build.gradle.kts
@web/orval.config.ts
@web/src/shared/api/demoRoles.ts
@web/src/pages/home/ui/HomePage.tsx

The existing webBuild inputs track VITE_DOCS_BASE and the production env files. Vite exposes loadEnv for values needed during config evaluation. The BFF publishes one OpenAPI 3.1 operation. Its component suite resolves the packaged response schema with NetworkNT and compares the served contract byte-for-byte. The client suite goes through Orval's generated runtime validation. [Vite configuration](https://vite.dev/config/#using-environment-variables-in-config) · [OpenAPI Schema Object](https://spec.openapis.org/oas/v3.1.0.html#schema-object)
</context>

<tasks>
<task type="tracer">
  <name>Resolve the documentation base before Vite builds or serves the app</name>
  <files>web/vite.config.ts, web/src/app/main.tsx, web/test/client-graph.py</files>
  <action>Resolve VITE_DOCS_BASE before the existing build branch in defineConfig. Use loadEnv with the active mode and the web project's effective env directory, preserving Vite's process environment and mode-file precedence. Give the resolved URL a single owner in the configuration. Parse the documented absolute HTTP(S) documentation URL, preserve the default http://127.0.0.1:8081/ and directory paths, and normalize the trailing slash once. Pass the resulting href into the app through Vite's define replacement for the individual import.meta.env key. Keep the app-to-HomePage URL interface and the existing loopback BFF proxy behavior. On parse or validation failure throw a fixed diagnostic naming VITE_DOCS_BASE and the expected URL form. Omit supplied values and underlying exceptions carrying raw input.

Extend the disposable project in web/test/client-graph.py with a compact config regression alongside its existing real webBuild check. Exercise the unset default and a valid prefixed deployment base, including slash normalization and the normalized href in the built entry asset. Starting from a clean output directory in the disposable copy, require a malformed port supplied in the process environment to fail the real build before output. Use a synthetic sentinel in the invalid value and check it stays out of the error. Exercise a malformed mode-specific env file with the variable absent from the subprocess environment, then override that same file with a valid process value and verify the shipped prefix. Prove that development also terminates during config evaluation on an invalid effective setting, using the real Vite dev entry with a bounded wait and cleanup. Keep all env files, outputs and child environments isolated from the working checkout. Reuse the existing Gradle invalidation entry point and managed Vite installation.</action>
  <verify><automated>./gradlew --console=plain :web:verifyClientGraph</automated></verify>
  <done>The production bundle contains the expected normalized root or prefix. An invalid active setting yields a named build or dev startup error without disclosing the supplied URL. An environment override takes precedence over the mode file.</done>
</task>

<task type="auto" tdd="true">
  <name>Publish the role string constraints and verify both contract consumers</name>
  <files>bff/src/main/resources/static/openapi.json, bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt, web/test/generated-client.test.ts</files>
  <behavior>For administrator.id, administrator.label, students[0].id and students[0].label, a value containing only a space and a tab fails validation. A string with whitespace and visible content is returned unchanged. Empty student arrays and student order remain valid.</behavior>
  <action>Extend the existing generated-client tests using their mocked fetch and loadDemoRoles path. Require the actual generated validator's ZodError for each changed field. In DirectoryHttpTest exercise responseSchema against copies of an otherwise valid response, changing one field per case and checking the pattern violation at that field. Run the negative cases before changing the contract. In both role schemas retain minLength and add the unanchored non-whitespace pattern (regex <code>\S</code>, JSON string <code>"\\S"</code>) to id and label. Verify the emitted Orval code by executing the generated-client tests after regeneration. Describe exact, case-sensitive ID uniqueness across the administrator and every student in the directory schema and the successful response description. JSON Schema uniqueItems compares entire array elements and cannot enforce this property across the directory. Leave the single listDemoRoles operation, artifact publication and generation inputs intact per D-03 and D-04.</action>
  <verify><automated>./gradlew --console=plain :bff:componentTest :web:generateClient :web:webCheck</automated></verify>
  <done>The canonical packaged and served contract match. Both independent validators reject the four whitespace-only cases and accept the positive controls. The contract describes the semantic uniqueness rule explicitly.</done>
</task>

<task type="auto" tdd="true">
  <name>Enforce directory identity at construction and exercise shell recovery</name>
  <files>bff/src/main/kotlin/courses/bff/BffApplication.kt, bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt, web/test/role-states.test.tsx</files>
  <behavior>A directory rejects two students with the same ID and different labels, and a student sharing the administrator's ID. Case-distinct IDs are accepted. Mutating the caller's original list cannot change a published directory. An HTTP 200 directory with a whitespace-only label or a duplicate ID produces the recoverable shell error.</behavior>
  <action>At DemoRoleDirectory construction, snapshot the ordered student roles into an unmodifiable list and validate that exact IDs are unique over that snapshot and the administrator. Preserve the controller's construction path, property names, valid fixture values, role order and JSON shape. Keep the model immutable and avoid alternate construction paths that allow an invalid list to escape. Use the existing DemoRole construction boundary to reject blank IDs and labels in server-owned role data. Cover invalid otherwise well-formed roles and directories, case-sensitive controls and mutation after construction in DirectoryUnitTest. Retain the existing client adapter's Set check and both existing adapter duplicate tests.

Add a whitespace-only label response to the existing failureResponses table in role-states.test.tsx. Reuse its duplicate response, saved-role assertion, disabled selector, alert and documentation navigation checks. Make an existing retry-to-success path start with one of these malformed HTTP 200 payloads and demonstrate that a valid reply restores the saved role. Keep the test in the existing shellSmoke runner per D-01, D-02 and D-06.</action>
  <verify><automated>./gradlew --console=plain :bff:test :bff:componentTest :web:webCheck :web:shellSmoke</automated></verify>
  <done>Both duplicate scenarios are rejected before a directory can be served. The saved selection survives a malformed reply and becomes selectable after retry. The live BFF still returns the documented roles in order.</done>
</task>
</tasks>

<threat_model>
| Threat ID | Category | Component | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-261126-lmn-01 | Information disclosure | Config error output | Low | mitigate | Use a fixed diagnostic and assert a synthetic sentinel is absent. |
| T-261126-lmn-02 | Tampering | Role directory response | Medium | mitigate | Validate nonblank fields and directory-wide identity at the producer and consumer boundaries. |
| T-261126-lmn-SC | Tampering | Dependency installation | Low | accept | The plan uses the existing locked toolchain. |
</threat_model>

<verification>
The disposable Gradle graph check covers WR-01. The BFF unit and HTTP tests, generated-client checks and existing shell smoke cover WR-02. Run git diff --check and the repository style check on the combined changes. Record the tested commands and outcomes in the quick summary.
</verification>

<success_criteria>
Invalid configuration fails before the browser receives a broken shell. Blank fields and duplicate identities have reproducible tests at their enforcing boundaries, and the reader can recover from a bad response through the existing retry action.
</success_criteria>

<output>
Create .planning/quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md after execution.
</output>
