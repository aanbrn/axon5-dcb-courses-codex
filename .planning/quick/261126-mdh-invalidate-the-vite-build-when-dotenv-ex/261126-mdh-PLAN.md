---
phase: quick-261126-mdh
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - web/build.gradle.kts
  - web/test/client-graph.py
autonomous: true
requirements: [FND-06]
estimate:
  tokens: 6500
  raw_tokens: 6500
  tasks: 2
  confidence: low
must_haves:
  truths:
    - Changing only an inherited dotenv expansion variable updates the documentation URL in the JavaScript loaded by the production shell.
    - Changing only an inherited port to an invalid value fails webBuild with the fixed Vite diagnostic and keeps the supplied value out of command output.
    - A repeated default production build is UP-TO-DATE. An explicit environment override still wins over the file, and an explicitly empty override still fails.
  artifacts:
    - path: web/build.gradle.kts
      provides: Conditional production bundle reuse based on the presence of production dotenv files
    - path: web/test/client-graph.py
      provides: Disposable production builds with task outcomes and emitted-entry assertions
  key_links:
    - from: web/build.gradle.kts
      to: web/vite.config.ts
      via: webBuild executes managed Vite to resolve and validate the effective documentation URL
    - from: web/test/client-graph.py
      to: web/build.gradle.kts
      via: Candidate.gradle invokes the wrapper and frontend_assets follows the production HTML entry
---

<objective>
Make `:web:webBuild` reflect the environment used by Vite to expand production dotenv files. The reviewer reproduced an unchanged task and stale `/first/` bundle at `cca11b1` after changing only `DOCS_PREFIX` to `second`.
</objective>

<context>
@web/build.gradle.kts
@web/test/client-graph.py
@web/vite.config.ts

Vite loads four dotenv files in production mode, expands references and gives process overrides priority. Gradle's execution-time `TaskOutputs.upToDateWhen` predicate can force the task to execute and prevent build-cache loads. The pinned NodeTask has no cacheable-task annotation and this build does not opt it into output caching. Use the single predicate on the existing file collection. This avoids another Node invocation to resolve inputs and keeps inherited expansion values out of Gradle input properties. [Vite environment loading](https://vite.dev/guide/env-and-mode#env-files) · [Gradle task output reuse](https://docs.gradle.org/current/kotlin-dsl/gradle/org.gradle.api.tasks/-task-outputs/up-to-date-when.html) · [NodeTask 7.1.0](https://github.com/node-gradle/gradle-node-plugin/blob/7.1.0/src/main/kotlin/com/github/gradle/node/task/NodeTask.kt)
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Rebuild the production entry when an inherited path changes</name>
  <files>web/test/client-graph.py, web/build.gradle.kts</files>
  <behavior>In the disposable candidate, clear the direct VITE_DOCS_BASE override. Write web/.env.production once with the literal VITE_DOCS_BASE=https://docs.example.test:${DOCS_PORT}/${DOCS_PREFIX}/. Set DOCS_PORT to 443 and DOCS_PREFIX to first, build, and verify the canonical /first/ URL in the loaded entry. Change only DOCS_PREFIX to second, reuse the same project and distribution, and require an EXECUTED bundle with the canonical /second/ URL.</behavior>
  <action>Extend verify_docs_base and use the existing Candidate helpers. Observe the stale second build before changing Gradle. In the webBuild registration, bind the existing project-root file tree for .env, .env.local, .env.production and .env.production.local to a local value. Retain its path-sensitive input declaration. Add an outputs.upToDateWhen predicate that checks whether this same file tree is empty at execution time. Include a short comment explaining that any production dotenv file can reference an inherited variable and therefore forces the bundle to execute, even for unchanged file contents or a direct override. Keep the direct docsBase input with its absent-versus-empty encoding and leave resolution and validation in Vite. Keep the predicate local to webBuild. No process environment enumeration, additional parser, subprocess for fingerprinting, or new dependency is needed.</action>
  <verify><automated>python3 web/test/client-graph.py --invalidation</automated></verify>
  <done>The same production dotenv bytes and direct setting produce two executed bundles with the expected distinct URLs. Default URL, direct precedence and explicitly empty override checks pass.</done>
</task>

<task type="auto" tdd="true">
  <name>Prove invalid inherited values reach validation and default builds retain incremental reuse</name>
  <files>web/test/client-graph.py</files>
  <behavior>After the successful second build, change only DOCS_PORT to a synthetic malformed port with a unique marker. Keep the candidate, dotenv file and previous output intact. The next build fails at webBuild with DOCS_DIAGNOSTIC, and the marker is absent from combined output. With no production dotenv file or direct override, a repeated bundle reports UP-TO-DATE and the loaded entry retains the default URL.</behavior>
  <action>Check rejection through Candidate.gradle's fails_with and excludes arguments so output is screened before printing. Test the no-file repeat in the candidate before the direct-empty override and before introducing any dotenv file. Keep the current contract generation, regeneration, invalid file, direct override and Vite dev controls. Exercise the inherited-value sequence with Gradle's build cache enabled by selecting the build-cache flag on those calls through the existing helper. Preserve its existing disabled-cache default everywhere else. Keep --no-configuration-cache independent of the output-cache flag. Verify the sequence runs without cleaning or forcing tasks. Keep private machine dotenv files excluded from the source copy.</action>
  <verify><automated>python3 web/test/client-graph.py --invalidation</automated></verify>
  <done>The harness verifies a successful changed URL, an invalid expanded port after a successful build, a non-disclosing diagnostic, and an unchanged default build that skips bundling.</done>
</task>

</tasks>

<threat_model>

| Threat ID | Boundary | Category | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-mdh-01 | Inherited settings to production bundle | Tampering | medium | mitigate | Require Vite execution for production dotenv files and assert both the loaded URL and rejection after an inherited-only change. |
| T-mdh-02 | Malformed input to build log | Information disclosure | medium | mitigate | Use a fixed validation message and check the captured output for the private test marker before printing. |
| T-mdh-SC | Build dependencies | Tampering | low | accept | The existing wrapper, managed Node and npm lock supply the entire check. |

</threat_model>

<verification>
Run the invalidation suite from the checkout root. Record the initial stale task outcome and final valid, invalid and default outcomes in the quick summary, using synthetic URLs and the fixed diagnostic.
</verification>

<success_criteria>
Inherited dotenv changes reach the actual Vite production entry and its validation on repeated Gradle invocations. The default no-file build remains incremental, and the existing generated-client and override contracts pass.
</success_criteria>

<output>
Create .planning/quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md after execution.
</output>
