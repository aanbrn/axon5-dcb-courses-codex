---
phase: 01-axon-server-and-toolchain-feasibility
reviewed: 2026-11-25T00:14:26Z
depth: standard
files_reviewed: 28
files_reviewed_list:
  - .gitignore
  - .java-version
  - .nvmrc
  - AGENTS.md
  - docs/feasibility/phase-01.md
  - gradle/libs.versions.toml
  - gradle/wrapper/gradle-wrapper.properties
  - mise.toml
  - probe/README.md
  - probe/build.gradle.kts
  - probe/kdoc/Specimen.kt
  - probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt
  - probe/src/integrationTest/kotlin/probe/ProbeFixture.kt
  - probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt
  - probe/src/main/kotlin/probe/ProbeApplication.kt
  - probe/src/main/kotlin/probe/ProbeProjection.kt
  - probe/src/test/kotlin/probe/ProbeContractsTest.kt
  - probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt
  - probe/typeid/check-vectors.ts
  - probe/typeid/package.json
  - probe/typeid/vectors.json
  - probe/verify_evidence.py
  - probe/verify_secondary.py
  - probe/web/build.gradle.kts
  - probe/web/build.mjs
  - probe/web/package.json
  - probe/web/settings.gradle.kts
  - settings.gradle.kts
findings:
  critical: 1
  warning: 3
  info: 0
  total: 4
  necessity: 0
status: issues_found
---

# Phase 01 Code Review Report

**Reviewed:** 2026-11-25T00:14:26Z

**Depth:** standard

**Files reviewed:** 28

**Status:** issues_found

## Summary

Reviewed phase head `7cbc414`. The milestone-bound scope resolver reported `degraded` with `no-task-commit-rows` and supplied the phase-range file union. The review cross-checked that union against the implementation diff and the two Guava fixes. The generated Gradle launchers and wrapper JAR are outside the source findings. Both npm lockfiles were inspected as supporting evidence.

The secondary verifier self-test passed. The report verifier accepted the retained `acceptance-5zjznvdt` evidence on Python 3.9.6 and 3.12.1. The Kotlin tests exercise the remote write, typed server rejection, independent durable reads, projection update, and controlled cleanup. The retained ARM64 run supports the required DCB feasibility result, and its successful secondary producers support their reported results. Four secondary attempt records misstate tool provenance. The `Blocked` finding can affect acceptance of a future non-passing stage.

The retained dependency graphs select Guava `33.8.0-android` in the consuming role and test configurations and `33.8.0-jre` in the formatter. The TypeID source uses the fixed-byte and string APIs covered by the dated, sample-specific npm advisory assessment. Private JVM advisory coverage and AMD64 runtime verification remain open in the feasibility record.

## Narrative Findings (AI reviewer)

**Critical Issues**

### CR-01: Distinct failures can satisfy the repeated blocker requirement

**Severity:** BLOCKER

**File:** `probe/verify_secondary.py:429-436`, `probe/verify_secondary.py:529-538`, `probe/verify_evidence.py:389-405`

**Issue:** The signature search matches Gradle's generic `> Task … FAILED` line before it reaches the cause. A local fixture gave the verifier two `:probe:kdocProbe` failures with the same exit code. One reported a changed KDoc paragraph and the other a formatter class-loading failure. `validate_record` accepted `Blocked` because both attempts had the same generic task line. The automatic capture can therefore accept a non-passing secondary stage without the two comparable failures required by the phase. The environmental signature also matches a missing fixture file through the broad `no such file or directory` pattern.

**Fix:** Use the first concrete error under Gradle's `What went wrong` section or an explicit failure emitted by the stage. Reject task summaries and generic banners as blocker signatures. Require an identified external dependency, launch error, or network diagnostic for an environmental disposition. Add self-test cases for different causes under the same failed task and for a missing fixture file.

**Warnings**

### WR-01: Secondary attempts record ambient Node and npm versions

**Severity:** WARNING

**File:** `probe/verify_secondary.py:342-365`, `probe/verify_secondary.py:541-551`, `probe/verify_evidence.py:108-119`

**Issue:** `current_tools` resolves `node` and `npm` from the verifier's `PATH` after the attempt. The direct fixture prepends Gradle's provisioned tools inside its child shell, and the Gradle tasks use the nested Node plugin. The four relevant attempt records in `acceptance-5zjznvdt` contain Node `v24.20.0` and npm `11.19.0`. The successful frontend-assets and TypeID producer observations record Node `v26.13.1` and npm `12.2.3`. The frontend-image stage uses the same provisioned static build and the direct fixture checks the selected versions in its build process. The manifest currently verifies with conflicting attempt metadata. The same ambient lookup also supplies the versions used to compare failing attempts.

**Fix:** Emit stage-specific versions from the executing command or record an executable-backed preflight using that command's environment. Bind those measurements to each attempt and check them against the producer observations. Keep a tool unresolved when the attempt fails before it can run. Capture new evidence after changing the verifier.

### WR-02: The documented Python floor rejects valid Java timestamps

**Severity:** WARNING

**File:** `probe/verify_secondary.py:109-112`, `docs/feasibility/phase-01.md:38`, `probe/README.md:39`

**Issue:** The guide supports Python 3.9, whose `datetime.fromisoformat` rejects Java `Instant` values with nine fractional digits. A direct check on Python 3.9.6 failed on `2026-11-25T00:00:00.123456789Z`. The Kotlin core transcript and image timestamp use `Instant.toString()` and can emit that precision. On such a host, a passing native suite can fail evidence verification. The retained macOS run contains six fractional digits.

**Fix:** Normalize the fractional component to microseconds before parsing, with coverage for zero, three, six, and nine fractional digits on Python 3.9. Raising the documented and checked interpreter minimum to Python 3.11 also resolves the incompatibility.

### WR-03: The frontend asset verifier accepts a contradictory staged hash

**Severity:** WARNING

**File:** `probe/verify_secondary.py:438-443`, `probe/verify_secondary.py:587-590`, `probe/web/build.gradle.kts:155-171`

**Issue:** The Gradle producer records `stagedSha256` and saves the staged HTML to `frontend-assets.html`. The verifier checks the hash's format and checks that the artifact is unchanged, but never compares the two values. A local fixture supplied a syntactically valid all-zero staged hash and a different HTML artifact hash. Both pass checks accepted the record. The retained acceptance record has matching values.

**Fix:** Require the `frontend-assets.html` snapshot and compare its SHA-256 with `stagedSha256` in `check_pass_artifacts`. Exercise a mismatched staged hash in the verifier self-test.

---

_Reviewed 2026-11-25T00:14:26Z_

_Reviewer gsd-code-reviewer_

_Depth standard_
