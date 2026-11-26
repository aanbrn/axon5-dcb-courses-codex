---
phase: quick-261126-lmh
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - tools/qodana-scan.sh
  - docs/maintainer-guide.md
autonomous: true
requirements: [QA-07]
estimate:
  tokens: 11500
  raw_tokens: 11500
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "The ordinary launcher recovers genuine Gradle diagnostics on e434f25, on the exact delivery commit and on a second scan of e434f25, with one shared analysis cache throughout."
    - "Every archived revision omits the checkout's Project_Default.xml before the scratch Git snapshot. Old cached editor settings cannot enter either the Spring-configured or unconfigured analysis path."
    - "The configured revisions use the same Spring Bean entry points, Axon plugin, warm Gradle dependencies and qodana.recommended profile. The working checkout retains its IDEA settings."
  artifacts:
    - path: tools/qodana-scan.sh
      provides: "Revision-bound archive exclusion and distinct analysis-cache generation"
    - path: docs/maintainer-guide.md
      provides: "Current Qodana snapshot and cache behavior"
  key_links:
    - from: tools/qodana-scan.sh
      to: .idea/inspectionProfiles/Project_Default.xml
      via: "Git archive excludes the literal editor profile before extraction"
    - from: tools/qodana-scan.sh
      to: .qodana/profiles/spring-beans.xml
      via: "The inspected blob supplies misc.xml and identifies the analysis cache within the new namespace"
    - from: tools/qodana-scan.sh
      to: qodana.yaml
      via: "The inspected configuration blob selects the existing installed-plugin cache"
---

<objective>
Close Phase 02 CR-04. A maintainer running the ordinary Qodana launcher on a historical commit must see the applicable recommended inspections even when the commit tracks an editor profile or the old cache contains that profile.
</objective>

<execution_context>
@.codex/gsd-core/workflows/execute-plan.md
@.codex/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-build-and-ui-foundations/02-REVIEW.md
@.planning/quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md
@.planning/quick/261126-jp0-recognize-spring-bean-entry-points-in-qo/261126-jp0-SUMMARY.md
@tools/qodana-scan.sh
@docs/maintainer-guide.md

The retained failing run is .gradle/qodana/runs/e434f250f5e3d729f789de1cb4dae2a5871080df.aLTXc4. The clean reference is .gradle/qodana/runs/fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq. Both declare a successful recommended inspection. The first returned zero findings and the second returned 51 genuine Gradle UnstableApiUsage results across 20 imported modules. The earlier fresh analysis also found getSuites() at build-logic/src/main/kotlin/courses.jvm.gradle.kts:24.
</context>

<tasks>
<task type="tracer">
  <name>Isolate the snapshot and recover diagnostics on the first historical scan</name>
  <files>tools/qodana-scan.sh, docs/maintainer-guide.md</files>
  <action>Keep the existing commit resolution and run-record convention. At the git archive call, retain the output tar and resolved revision and add the root include and quoted Git exclusion pathspec after the revision: -- . ':(top,exclude,literal).idea/inspectionProfiles/Project_Default.xml'. This was checked on e434f25, fff0b35, b838a25 (no editor profile) and the planning base 9bac742. The Git tree walk preserves all other archived files and honours the revision's own export attributes. It never follows archived symlink ancestors to delete a file. Keep the existing scratch Git initialization and Spring misc.xml collision checks.

Choose .gradle/qodana/analysis-cache/without-editor-profile/ as a fresh analysis namespace. Before the Spring branch give the entry-point key the value no-entry-points. In the existing branch resolve that key from the revision's XML blob and install the blob as before. After the branch create the analysis directory under the new namespace for either key. Preserve the exact Gradle cache location, plugin blob key and no-config fallback, lock, mounted paths, image selection, Temurin feature and scanner options. Leave the old analysis directories in place. Correct the Qodana cache and archive sentences in the maintainer guide, including its description of scans without the Spring XML. Limit changes to those sentences.

Start the three-run sequence here. Use the updated ordinary launcher from this checkout, Docker and the existing warm Gradle/plugin directories. Keep per-run console logs under ignored .gradle/qodana/261126-lmh/ and take the run directory from the launcher's printed report path. Record the host editor profile digest and the existing Gradle/plugin cache identities before the first run. Run e434f25 once and retain its run directory as FIRST_RUN for Task 2. Check the revision marker, the local Git snapshot tree and the working snapshot after Qodana exits. Check the new analysis cache after this and each subsequent scan for the editor profile. Confirm representative Gradle findings before committing the launcher and guide together. Capture the full SHA of that commit as DELIVERY for the next scan.</action>
  <verify>
    <automated>sh -n tools/qodana-scan.sh && mise exec shellcheck -- shellcheck tools/qodana-scan.sh</automated>
    <automated>mkdir -p .gradle/qodana/261126-lmh && mise exec python -- sh tools/qodana-scan.sh e434f25 > .gradle/qodana/261126-lmh/first.log 2>&1</automated>
    <automated>jq -e 'any(.runs[].results[]; .ruleId == "UnstableApiUsage" and (.message.text | contains("@Incubating")) and .locations[0].physicalLocation.artifactLocation.uri == "bff/build.gradle.kts")' "$FIRST_RUN/results/qodana.sarif.json"</automated>
  </verify>
  <done>The real historical scan reports a BFF Gradle incubation finding. Its synthetic snapshot and new analysis cache omit the editor profile. The documented configured and unconfigured cache selections both bypass the old analysis data.</done>
</task>

<task type="auto">
  <name>Prove isolation across the delivery commit and a return to the historical revision</name>
  <files>.planning/quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-SUMMARY.md</files>
  <action>Continue with the exact implementation commit recorded as DELIVERY, then run e434f25 again. Use the same checkout and launcher as Task 1, in sequence with the existing scan timeout, keeping all caches and run outputs in place. Obtain MIDDLE_RUN and LAST_RUN from their respective console logs. Keep the SARIF, module reports, logs and scratch snapshots under the ignored run directories. The retained zero-result report supplies the negative control.

For each of the three new run directories, require its revision file to equal the full requested SHA. Inspect the synthetic Git tree for absence of the editor-only file, inspect the extracted project after the scan and check the shared new analysis-cache subtree for any persisted .idea/inspectionProfiles/Project_Default.xml. Confirm the Spring blob key is identical across the three revisions, the generated project misc.xml contains org.springframework.context.annotation.Bean and the log records the loaded Axon plugin. Check that the three factory methods and four Axon handlers from the prior qualification retain their expected inspection behavior. Compare the host editor profile digest and cache identities with the pre-run observations.

Compare each SARIF against the clean fff0b35 run. Require a nonempty invocation list, successful execution, the recommended profile, success of Gradle import in the log and the same 20 modules. Match the 51 known diagnostics by rule, file, line/column, highlighted token and message. Record any additional findings, including the documented fresh-cache getSuites() diagnostic. Investigate a missing known result, changed module model or new engine/import error before accepting a run. Record the comparable SARIF notifications separately from findings, including the previously reported generated-root sanityFailure. Write the three revisions, run directories, finding counts, differences, cache checks, plugin version and local style result into the quick summary.</action>
  <verify>
    <automated>mise exec python -- sh tools/qodana-scan.sh "$DELIVERY" > .gradle/qodana/261126-lmh/middle.log 2>&1</automated>
    <automated>mise exec python -- sh tools/qodana-scan.sh e434f25 > .gradle/qodana/261126-lmh/last.log 2>&1</automated>
    <automated>jq -es 'def records: [.runs[].results[] | [.ruleId,.locations[0].physicalLocation.artifactLocation.uri,.locations[0].physicalLocation.region.startLine,.locations[0].physicalLocation.region.startColumn,.locations[0].physicalLocation.region.snippet.text,.message.text]]; (.[0] | records) as $known | length == 4 and ($known | length) == 51 and all(.[1:][]; (.runs | length) == 1 and all(.runs[]; .properties.configProfile == "recommended" and (.invocations | length) > 0 and all(.invocations[]; .executionSuccessful)) and (($known - records) | length) == 0)' .gradle/qodana/runs/fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq/results/qodana.sarif.json "$FIRST_RUN/results/qodana.sarif.json" "$MIDDLE_RUN/results/qodana.sarif.json" "$LAST_RUN/results/qodana.sarif.json"</automated>
    <automated>jq -es 'length == 4 and all(.[]; (.modules | length) == 20) and (map(.modules | sort) | unique | length) == 1' .gradle/qodana/runs/fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq/results/projectStructure/Modules.json "$FIRST_RUN/results/projectStructure/Modules.json" "$MIDDLE_RUN/results/projectStructure/Modules.json" "$LAST_RUN/results/projectStructure/Modules.json"</automated>
    <automated>
set -eu
policy=.idea/inspectionProfiles/Project_Default.xml
historical=$(git rev-parse --verify 'e434f25^{commit}')
first_sha=$(cat "$FIRST_RUN/revision")
middle_sha=$(cat "$MIDDLE_RUN/revision")
last_sha=$(cat "$LAST_RUN/revision")
test "$first_sha" = "$historical"
test "$middle_sha" = "$DELIVERY"
test "$last_sha" = "$historical"
for run in "$FIRST_RUN" "$MIDDLE_RUN" "$LAST_RUN"; do
  tracked_profile=$(git -C "$run/project" ls-tree HEAD -- "$policy")
  test -z "$tracked_profile"
  test ! -e "$run/project/$policy"
  test ! -L "$run/project/$policy"
  rg -Fq org.springframework.context.annotation.Bean "$run/project/.idea/misc.xml"
done
cache=.gradle/qodana/analysis-cache/without-editor-profile
spring_blob=$(git rev-parse --verify "$historical:.qodana/profiles/spring-beans.xml")
test -d "$cache/$spring_blob"
cached_profiles=$(find "$cache" -path "*/$policy" -print)
test -z "$cached_profiles"
    </automated>
    <automated>git diff --check "$DELIVERY^..$DELIVERY" && mise exec python ruff taplo -- ./gradlew --console=plain styleCheck :docs-site:check</automated>
  </verify>
  <done>All three bound runs recover the known Gradle diagnostics with the same module structure, source-appropriate framework settings and warm dependency caches. The summary identifies their evidence and accounts for any differences.</done>
</task>
</tasks>

<threat_model>
| Boundary | Threat | Severity | Disposition and mitigation |
| --- | --- | --- | --- |
| Archived Git tree to inspection snapshot | T-lmh-01 Tampering by revision-owned editor policy or unsafe path traversal | High | Mitigate with the literal Git tree exclusion before extraction. Preserve the existing scratch settings collision checks. |
| Persisted analysis cache to subsequent scan | T-lmh-02 Tampering through restored IDEA settings | High | Mitigate with a fresh namespace for both Spring-keyed and unconfigured analyses. Measure the same cache after each of three scans. |
| Package inputs | T-lmh-SC Supply-chain tampering | Low | Accept the existing pinned scanner and qualified plugin setup. This change installs no new dependency. |
</threat_model>

<verification>
The three launcher commands form one chronological regression check. The executor runs each once and uses the checks above against those specific run directories. The historical negative and the clean 51-result reference remain available for direct comparison.
</verification>

<success_criteria>
The accepted Phase 02 review finding CR-04 is reproducibly closed by the ordinary launcher. The checked-in IDEA profile stays available to IntelliJ, and the Qodana guide accurately describes both analysis-cache paths.
</success_criteria>

<output>
Create .planning/quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-SUMMARY.md after verifying the delivery commit.
</output>
