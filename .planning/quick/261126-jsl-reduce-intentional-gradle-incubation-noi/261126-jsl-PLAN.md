---
phase: quick-261126-jsl
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - .idea/inspectionProfiles/Project_Default.xml
  - .gitignore
  - docs/maintainer-guide.md
  - tools/idea/gradle-inspections.xml
autonomous: true
requirements: [QA-07]
estimate:
  tokens: 16000
  raw_tokens: 16000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - A maintainer can use an IntelliJ IDEA project inspection profile that removes warnings caused by org.gradle.api.Incubating.
    - A Kotlin call to Guava's Beta-annotated Funnels.byteArrayFunnel still produces UnstableApiUsage with this profile.
    - The repository's ordinary Qodana scan still imports the Gradle project and reports incubating APIs.
  artifacts:
    - path: docs/maintainer-guide.md
      provides: How to select the qualified IDEA profile and recheck it on upgrades
  key_links:
    - from: docs/maintainer-guide.md
      to: tools/qodana-scan.sh
      via: Revision-scoped inspection for auditing Gradle wrapper upgrades
---

<objective>
Remove the editor warnings caused by the intentional use of Gradle's incubating APIs. Deliver a native IntelliJ project profile with the existing warning level and the remaining unstable annotations. The preferred delivery uses the standard Project Default file. The alternate XML path in the file list applies only if clean import or existing project settings require explicit project-level import.
</objective>

<context>
@AGENTS.md
@.planning/STATE.md
@.planning/quick/261126-i4h-resolve-actionable-qodana-findings/261126-i4h-SUMMARY.md
@.planning/quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md
@.gitignore
@docs/maintainer-guide.md
@tools/qodana-scan.sh

The earlier scan identified the JVM Test Suite DSL, configuration roles, fixture build paths and centralized repositories. The qualified Axon configuration reported 51 Gradle occurrences on its final warm scan and 52 in fresh scans. One observation of TestingExtension.getSuites() varied across identical call sites. Re-read HEAD, the launcher and qodana.yaml at execution because the separate Spring quick task may have landed. Use a before/after comparison on that actual starting revision.

Planning found the Toolbox-installed IntelliJ IDEA Ultimate 2026.3 build 263.7307.200 and its executable Contents/bin/inspect.sh in the user's Applications directory. The installed descriptor marks UnstableApiUsage enabled at WARNING. The installed inspection initializes its public List field with ExternalizableStringSet. The bundled IntelliJ XmlSerializer round-tripped that field shape as option[name=unstableApiAnnotations] / set / option[value]. The documented defaults include ten annotation names. No Project_Default.xml or profiles_settings.xml was present in the checkout at planning time. JetBrains documents the project-level profile, the distinct editor and batch selection mechanisms, and the native inspector. [Inspection defaults](https://www.jetbrains.com/help/inspectopedia/UnstableApiUsage.html) · [IDEA profiles](https://www.jetbrains.com/help/idea/customizing-profiles.html) · [IDEA offline inspector](https://www.jetbrains.com/help/idea/command-line-code-inspector.html) · [Qodana profiles](https://www.jetbrains.com/help/qodana/inspection-profiles.html)
</context>

<tasks>
<task type="tracer">
  <name>Qualify the project profile with a Gradle call and an external Guava call</name>
  <files>.idea/inspectionProfiles/Project_Default.xml and .gitignore on the default-profile path, or tools/idea/gradle-inspections.xml on the explicit-import path</files>
  <action>Record the execution-base SHA and inspect current tracked and ignored project profiles, their settings and the root ignore rules. Preserve opted-in project and personal settings. Under .gradle/idea-inspection/261126-jsl create disposable, clean Git snapshots of the execution base. Keep controls and IDE config, indexes, logs and reports disposable. Do not copy the working checkout's generated Gradle metadata or interrupt a running desktop IDE.

Create the candidate project profile in JetBrains' InspectionProjectProfileManager component, with a version 1.0 profile named Project Default. Configure only UnstableApiUsage, enabled at its existing WARNING level and enabled by default. Set unstableApiAnnotations using the serializer shape above. Retain the documented org.jetbrains.annotations.ApiStatus.ScheduledForRemoval, org.jetbrains.annotations.ApiStatus.Experimental, org.jetbrains.annotations.ApiStatus.Internal, com.google.common.annotations.Beta, io.reactivex.annotations.Beta, io.reactivex.annotations.Experimental, rx.annotations.Experimental, rx.annotations.Beta and org.apache.http.annotation.Beta. Check the actual build's defaults for additions. Remove exactly org.gradle.api.Incubating. Keep the other inspection options inherited. Make an otherwise identical baseline profile containing the original list. To prove that both profiles still diagnose an external library, add the same scratch-only Kotlin method calling com.google.common.hash.Funnels.byteArrayFunnel() in the probe to both copies. Funnels in the cataloged Guava release has @Beta. Add an explicit dependency using the existing catalog in both disposable copies if necessary for compilation. Keep real Gradle call sites in both.

Run the native offline inspector from the installed application's Contents/bin, with separate temporary IDE configuration/system/log paths, a working JDK and full Gradle import. Set IDEA_INSPECT to the discovered inspect.sh and use its documented project, profile and output arguments. Pass the control profile explicitly for the baseline and the candidate project profile for the treatment. Direct any absolute arguments required by the CLI to the current disposable directories. Check import, Kotlin module indexing and Gradle script analysis in both logs. Verify the same Guava location in both reports, real Gradle @Incubating diagnostics in the baseline and zero Gradle @Incubating diagnostics in the treatment. Startup success, zero results or an empty project model cannot establish selectivity. Check that a fresh checkout containing only the proposed tracked IDEA file still links the root and included builds, imports the intended modules and resolves the representative Gradle calls. Keep editor selection distinct from explicitly passing a batch profile.

If native offline inspection is unavailable or fails to import the two controlled projects, record the precise limitation. Use the same inspection in the pinned Qodana image with explicit scratch profile paths and full Gradle import. Use disposable copies of the current launcher to change only profile selection for this experiment. Keep JDK, Axon configuration, source controls and image equal. Obtain the same positive and negative results and record SARIF executionSuccessful, import logs, analyzer build and profile. Preserve the ordinary scanner separately for Task 2. If the clean checkout's seeded .idea directory interferes with import or a pre-existing profile would be overwritten, qualify tools/idea/gradle-inspections.xml for explicit project-level import with the same inspection and document the selection in Task 2. Prefer a minimal exported XML with a distinct name for that path. Commit one qualified delivery path only. For the preferred path replace the directory-wide ignore with rules that admit only .idea/inspectionProfiles/Project_Default.xml, keeping sibling profiles, workspace.xml, gradle.xml and the remaining local metadata ignored. Do not change Gradle build scripts, framework annotations or the Qodana launcher in the delivered checkout.</action>
  <verify>
    Run the first three commands on the native route and the SARIF command on the fallback route. Set CANDIDATE_PROFILE to the candidate XML, and the two report variables for the chosen route to its actual UnstableApiUsage.xml or qodana.sarif.json files.
    <automated>"$IDEA_INSPECT" .gradle/idea-inspection/261126-jsl/baseline .gradle/idea-inspection/261126-jsl/baseline-profile.xml .gradle/idea-inspection/261126-jsl/baseline-results -v2</automated>
    <automated>"$IDEA_INSPECT" .gradle/idea-inspection/261126-jsl/candidate "$CANDIDATE_PROFILE" .gradle/idea-inspection/261126-jsl/candidate-results -v2</automated>
    <automated>python3 -c 'import sys,xml.etree.ElementTree as E; records=lambda p: [(n.findtext("file","").split("/probe/")[-1],n.findtext("line"),n.findtext("description","")) for n in E.parse(p).iter("problem")]; a,b=map(records,sys.argv[1:]); gradle=lambda r: [x for x in r if "Incubating" in x[2]]; beta=lambda r: sorted((f,l,m) for f,l,m in r if "Beta" in m); assert gradle(a) and not gradle(b) and beta(a) and beta(a)==beta(b)' "$BASE_IDEA_REPORT" "$CANDIDATE_IDEA_REPORT"</automated>
    <automated>jq -es 'def findings($marker): [.runs[].results[] | select(.ruleId == "UnstableApiUsage" and (.message.text | contains($marker)))]; def control: findings("Beta") | map([.locations[0].physicalLocation.artifactLocation.uri, .locations[0].physicalLocation.region.startLine, .message.text]) | sort; all(.[]; all(.runs[].invocations[]; .executionSuccessful == true)) and ((.[0] | findings("Incubating") | length) > 0) and ((.[1] | findings("Incubating") | length) == 0) and ((.[0] | control | length) > 0) and ((.[0] | control) == (.[1] | control))' "$BASE_QODANA_REPORT" "$CANDIDATE_QODANA_REPORT"</automated>
  </verify>
  <done>The qualified profile filters the Gradle annotation and retains the observed Guava warning. A clean Gradle import covers the modules needed to reproduce both diagnostics. The versioned file and selection procedure fit the checkout's actual IDE settings.</done>
</task>

<task type="auto">
  <name>Verify ordinary Qodana coverage and document the IDEA setting</name>
  <files>docs/maintainer-guide.md, .planning/quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md</files>
  <action>Add a short maintainer note on the selected project profile, the exact inspection and annotation, the full project-wide scope of that exclusion, and the intentional suite and configuration role usages. Give the IDEA Settings → Editor → Inspections selection or project-level import steps if required. Include how to retain an existing custom selection and apply the one annotation edit to it. On Gradle wrapper upgrades, use the ordinary scan and build to review changed incubating call sites. On IDE upgrades compare the stored annotation list with the current bundled defaults. Fit the note around any separate Spring guidance already present.

Compare the ordinary launcher reports for the execution base and the committed implementation using the launcher's current explicit profile selection, plugin setup and revision markers. Reuse the preceding Spring task's clean final ordinary scan if its revision matches, or if the only intervening changes concern planning records and the launcher, profile and inspected sources match. Record that provenance. Run the baseline command only when a suitable report is absent. Always run the ordinary command on the committed delivery. Check the fresh candidate checkout import, the source/module coverage and the SARIF messages matched by rule, path and diagnostic. Compare the Gradle groups and account for any change in the optional suites accessor observation. Compare the non-Gradle findings with the ordinary baseline to catch profile selection or import changes. Reference the existing Spring verification for framework-specific evidence. Check Git ignores by testing the profile path and sample private paths with git check-ignore --no-index, plus git ls-files -- .idea. Run the repository style checks and documentation tests. Record reports, SHAs, IDE/Qodana builds, exact control diagnostics, run modes and import evidence in the quick summary. State whether the evidence covers native batch inspection, default selection in the live editor, or the Qodana inspection engine. Leave phase UAT and roadmap tracking to their own workflows.</action>
  <verify>
    <automated>mise exec python -- sh tools/qodana-scan.sh "$EXECUTION_BASE"</automated>
    <automated>mise exec python -- sh tools/qodana-scan.sh "$(git rev-parse HEAD)"</automated>
    <automated>mise exec python ruff taplo -- ./gradlew --console=plain styleCheck :docs-site:check</automated>
    <automated>git check-ignore --no-index .idea/workspace.xml &amp;&amp; git check-ignore --no-index .idea/gradle.xml &amp;&amp; git check-ignore --no-index .idea/inspectionProfiles/Other.xml</automated>
  </verify>
  <done>The ordinary reports retain the expected Gradle diagnostics at the real call sites and show successful imports. The documented profile location and selection match the delivered XML. Git exposes only the intended shared profile, or keeps all .idea metadata private with the explicit-import alternative. Style and docs checks pass. The summary distinguishes the measurements and any unverified editor interaction.</done>
</task>
</tasks>

<threat_model>
| Threat ID | Category | Component | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-261126-jsl-01 | Information disclosure | IntelliJ local project files | Low | mitigate | Check the exact allowlist and tracked file list before committing. |
| T-261126-jsl-02 | Tampering | Inspection coverage | Low | mitigate | Compare matched Gradle and external Guava findings under the two profiles and verify the ordinary runner separately. |
| T-261126-jsl-SC | Tampering | Inspection dependencies | Low | accept | The experiment uses the existing pinned analyzer, installed IDEA and cataloged Guava. |
</threat_model>

<verification>
Use results from comparable imported projects to establish the effect on the editor inspection. Use the ordinary revision-scoped launcher to verify independent scanner behavior. Include project selection evidence for a default-selection claim.
</verification>

<success_criteria>
A maintainer can select the verified native profile, work with the intentional Gradle APIs and still see other unstable API warnings. The ordinary Qodana scan provides an independent record of Gradle incubation for upgrade review.
</success_criteria>

<output>
Create .planning/quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md after execution.
</output>
