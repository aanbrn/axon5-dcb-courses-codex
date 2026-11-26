---
phase: quick-261126-ink
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - qodana.yaml
  - docs/maintainer-guide.md
  - tools/qodana-scan.sh # Only if a supported artifact mount qualifies.
  - gradle/libs.versions.toml # Only if that mount needs a catalog-owned pin.
  - .planning/quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md
autonomous: true
requirements: [QA-07]
estimate:
  tokens: 18000
  raw_tokens: 18000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - Maintainers can identify which framework entry points the pinned Community linter recognizes and reproduce the evidence locally.
    - Enabling Axon support requires a loaded plugin, a successful Gradle import, selective recognition of handlers, and a surviving unused-method control.
    - The local scan continues to work without credentials. The Spring edition and token prerequisites are documented.
  artifacts:
    - path: .planning/quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md
      provides: Runtime evidence, per-symbol comparison and disposition for both frameworks
  key_links:
    - from: tools/qodana-scan.sh
      to: gradle/libs.versions.toml
      via: The local scan selects the digest-pinned Community image and archives the requested Git commit.
---

<objective>
Qualify the Axon Framework plugin on the repository's Kotlin probe and establish the prerequisites for Spring inspections. Publish the smallest configuration supported by the results.
</objective>

<context>
@.planning/quick/261126-i4h-resolve-actionable-qodana-findings/261126-i4h-SUMMARY.md
@docs/maintainer-guide.md
@tools/qodana-scan.sh
@gradle/libs.versions.toml
@probe/src/main/kotlin/probe/ProbeApplication.kt
@probe/src/main/kotlin/probe/ProbeProjection.kt

JetBrains documents installation by Marketplace plugin ID and the plugin cache. [Plugin installation](https://www.jetbrains.com/help/qodana/extending-qodana-plugins.html) [Configuration reference](https://www.jetbrains.com/help/qodana/configuration-reference.html#Manage+plugins)

AxonIQ publishes plugin ID `io.axoniq.ide.intellij`. Stable release 0.10.1 corresponds to Marketplace update 1119101, since build 242.0, with platform, Java and Kotlin dependencies. The descriptor registers AxonImplicitUsageProvider. Qualify its effect on the pinned QDJVM-263.8362 Kotlin inspection. [Marketplace](https://plugins.jetbrains.com/plugin/18628-axon-framework) [Release](https://github.com/AxonFramework/IdeaPlugin/releases/tag/v0.10.1)

JetBrains lists Spring support in Qodana for JVM under Ultimate or Ultimate Plus. Running that linter requires an authorized QODANA_TOKEN. This environment has no such token. [JVM edition matrix](https://www.jetbrains.com/help/qodana/jvm.html#Supported+technologies+and+features) [Token requirements](https://www.jetbrains.com/help/qodana/docker-image-configuration.html)
</context>

<tasks>
<task type="tracer">
  <name>Measure the plugin's effect on the same Kotlin declarations</name>
  <files>.gradle/qodana/261126-ink/control, .gradle/qodana/261126-ink/candidate (disposable Git repositories)</files>
  <action>Create two disposable repositories from git archive c0006845dd626c484e904805610c84194f0342ad under the listed paths. Add the same ordinary unannotated Kotlin method next to ready in both snapshots, with matching visibility, an otherwise-used declaring class, and a distinctive method name. Commit each snapshot locally because the scanner reads committed files. Confirm both trees have identical Kotlin inputs. Use the repository launcher, recommended profile, native ARM64 catalog image, Temurin feature and Gradle wrapper in both. Each scratch repository owns its own plugin cache. Reuse dependency caches safely if necessary. The only candidate configuration difference should be a documented Marketplace declaration for io.axoniq.ide.intellij. Inspect the 2026.3 schema or implementation for a supported exact version or immutable artifact option. Use it if available, keep a single version owner, and avoid unsupported YAML fields. If resolution floats, record the actual artifact version and digest, and the implications for requalification. If the built-in mechanism fails, check the published artifact and supported local plugin mount in the disposable candidate to distinguish transport from incompatibility. Bound each scan to the existing 900000 ms analysis timeout plus a five-minute startup allowance, with at most one corrective retry for a diagnosed infrastructure error. Keep all reports local and authorize only the public release, inspected descriptor and pinned image.</action>
  <verify>
    <automated>mise exec python -- git -C .gradle/qodana/261126-ink/control -c 'alias.scan=!sh tools/qodana-scan.sh' scan HEAD</automated>
    <automated>mise exec python -- git -C .gradle/qodana/261126-ink/candidate -c 'alias.scan=!sh tools/qodana-scan.sh' scan HEAD</automated>
  </verify>
  <done>Identify the loaded ID and version from the candidate startup log or runtime plugin inventory. Inspect invocation status, Gradle import completion, analysis coverage, plugin errors and SARIF notifications. Compare diagnostic multisets by rule, path, symbol and message. Account separately for ready, enroll, course, enrolled, the Spring beans enrollmentHandler, tokenStore, courseProjection, the ordinary control, and every other diagnostic. The preceding source scan had 52 UnstableApiUsage results and a separate generated pluginUnderTestMetadata notice. The control must itself be reported in the baseline for the experiment to qualify. Record the failing step and evidence if the experiment cannot establish plugin behavior.</done>
</task>

<task type="auto">
  <name>Apply the qualified result and document Spring availability</name>
  <files>qodana.yaml and docs/maintainer-guide.md (qualified integration), tools/qodana-scan.sh and gradle/libs.versions.toml (qualified mount only), .planning/quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md</files>
  <action>If the candidate loaded successfully, recognized Axon handlers selectively, retained the ordinary finding, and preserved inspection coverage, enable the proven Marketplace setup in qodana.yaml, recording exactly which handler types benefit. Retain the catalog image as the sole linter pin and keep the recommended inspection profile. Explain plugin resolution and how to requalify it in the existing maintainer guide, with the Spring edition and token prerequisite. If the candidate needs a mounted artifact, first establish that the same supported pin and mount can operate reproducibly on a clean checkout with the existing launcher before adopting it. Any necessary launcher or catalog edit is conditional on that proof and should be limited to the verified pin and mount. Use no bespoke downloader, IDE installation or global state. Commit the integration before its final scan. If runtime evidence shows no viable integration, record that outcome in the quick summary and verify the existing baseline runner against the base revision. Distinguish an inconclusive download or import from a loaded plugin with no effect. Record revision markers, image and plugin identity, comparable local report paths, counts, every changed diagnostic, notices and the Spring prerequisite. Keep the experiment and any ordinary control out of tracked sources. Account creation, license changes, cloud reports, application edits, CI, inspection suppressions and milestone records are outside this task.</action>
  <verify>
    <automated>mise exec python -- sh tools/qodana-scan.sh "$(git rev-parse HEAD)"</automated>
    <automated>mise exec python ruff taplo -- ./gradlew --console=plain styleCheck</automated>
  </verify>
  <done>The actual launcher produces SARIF and HTML from the recorded implementation SHA, or from c0006845dd626c484e904805610c84194f0342ad on the feasibility-only path. Check the stored revision marker, successful invocation, import diagnostics and all seven original declarations on that scan. A delivered integration must show the claimed effects with no new plugin or import failure. The summary identifies measured Axon behavior and the outstanding Spring prerequisite; generated reports remain local.</done>
</task>
</tasks>

<threat_model>
| Threat ID | Category | Component | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-261126-ink-01 | Tampering | Analyzer plugin | Medium | mitigate | Verify the AxonIQ artifact, loaded version, resolution behavior and runtime evidence against the Marketplace record. |
| T-261126-ink-02 | Information disclosure | Scan inputs and results | Medium | mitigate | Use committed tracked sources and local result paths with the credential-free Community launcher. |
</threat_model>

<verification>
Use the scratch runs to establish causality and preserve the original runner's revision marker and SARIF for the final result. Compare the committed scan with the clean source baseline, excluding only the intentionally scratch-only control.
</verification>

<success_criteria>
Every claimed framework capability has observed evidence or a named prerequisite. Any enabled plugin works through the ordinary revision-scoped command and repository style checks pass.
</success_criteria>

<output>
.planning/quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md
</output>
