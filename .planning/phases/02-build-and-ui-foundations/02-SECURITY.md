---
phase: "02"
slug: "build-and-ui-foundations"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-11-25"
---

# Phase 02 — Security

The audit reviewed implementation at `d4ea692` against the 19 authored threats. The blocking threshold was high.

## Trust Boundaries

| Boundary | Data crossing |
| --- | --- |
| Contract to build and browser | Checked-in OpenAPI, generated client, and role directory JSON |
| Index to formatting and publication | Staged file bytes, paths, modes, and configuration |
| Repository to docs output | Explicit public content and static assets |
| Dependencies and CI | Registry artifacts, tracked locks, Action pins, and runner inputs |

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| T-02-01 | Spoofing / Tampering | Role response | high | mitigate | Generated Fetch schema validation and a live response-to-DOM comparison in `web/test/role-tracer.mjs`. | closed |
| T-02-02 | Tampering | Generated client | medium | mitigate | Declared contract input and clean, unchanged, deleted, and renamed-contract checks in `web/test/client-graph.py`. | closed |
| T-02-03 | Disclosure / Tampering | Test fixtures | medium | mitigate | `verifyFixtureIsolation` verifies both suite variants and excludes test dependencies from production runtime. | closed |
| T-02-04 | Tampering | HTTP schema | high | mitigate | `DirectoryHttpTest` validates the served response and rejects missing data and external schema references. | closed |
| T-02-05 | Spoofing | Tab-local persona | medium | mitigate | Exact ID reconciliation after a valid directory response and tests for stale IDs and blocked storage. | closed |
| T-02-06 | Tampering | Role retry | medium | mitigate | Single active request, stale-result guard, and Chromium checks for focus during recovery. | closed |
| T-02-07 | Information disclosure | Docs publication | high | mitigate | Canonical source allowlist and negative tests for unexpected paths and synthetic private bytes. | closed |
| T-02-08 | Tampering | Docs launch configuration | medium | mitigate | Validated launch scheme, credentials, allowed origins and deployment base, with both launch modes tested. | closed |
| T-02-09 | Tampering | Kotlin quality | medium | mitigate | ktfmt, detekt and Dokka checks catch controlled violations and pass after repair. | closed |
| T-02-10 | Tampering | UI source and role labels | high | mitigate | Official radix-nova registry provenance and Chromium test for markup-like text rendered literally. | closed |
| T-02-11 | Tampering | Architecture and accessibility | medium | mitigate | `foundationProof` requires the named Steiger and axe failures and successful repair. | closed |
| T-02-12 | Tampering | Staged Git index | high | mitigate | Candidate snapshot, exclusive index lock, identity check and atomic replacement, with preservation and writer tests. | closed |
| T-02-13 | Elevation of privilege | Style paths and configuration | high | mitigate | NUL-delimited Git paths and argument arrays, with candidate-config and metacharacter path fixtures. | closed |
| T-02-14 | Spoofing | Tool readiness | medium | mitigate | `doctor` observes managed and JVM worker versions and detects a wrong required tool. | closed |
| T-02-15 | Information disclosure | Private advisory evidence | high | mitigate | Public-only graph workflow and documentation tests that verify synthetic private evidence is excluded. | closed |
| T-02-16 | Tampering | Build graph | medium | mitigate | Clean build harness checks real artifacts, producer ordering, stable locks and absence of infrastructure tasks. | closed |
| T-02-17 | Elevation of privilege / Information disclosure | PR workflow | high | mitigate | Read-only permissions, full Action SHAs, no persisted credentials and wrapper-first validation. The matched hosted run remains a ship gate. | closed |
| T-02-18 | Spoofing / Tampering | Generated runtime adapter | high | mitigate | Generated Zod validation and tests rejecting redirects, wrong status/media, duplicate IDs and malformed JSON. | closed |
| T-02-SC | Tampering | Build and package inputs | high | mitigate | Exact reviewed inputs, managed npm ci with install scripts disabled, lock origin/integrity checks and scoped Maven/tool constraints. | closed |

The auditor independently ran the local workflow parser, lock integrity checks for five npm locks, and publication verification against the five emitted documentation artifacts. Retained JUnit XML showed two unit and four component tests with zero failures, errors, or skips.

## Review Follow-Up

The 18-case Chromium rerun verified recovery from stalled response bodies for T-02-06. The docs suite and prefixed Chromium journey retained the publication and launch constraints for T-02-07 and T-02-08. The published tree now adds exactly two whitelisted WOFF2 files and their licenses. The two resolved font tarballs and integrity values match the web lock, and all retained docs lock entries match their prior values. npm pruned 15 entries marked extraneous.

Fourteen real Git cases and the post-clean commit exercise verified index-only formatting, preserved editor and shell bytes, and refusal of unformatted path-limited commits for T-02-12 and T-02-13. The comma-bearing-source test and staged policy still validate authored Kotlin. The original unwrapped feasibility specimen receives the tracked plain-text check and is formatted only in a build copy. Six doctor self-tests include missing and invalid Node pins for T-02-14. The workflow checker and actionlint passed for T-02-17, including local rejection of write permissions and unpinned Actions.

## Accepted Risks Log

No accepted risks.

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
| --- | --- | --- | --- | --- |
| 2026-11-25 | 19 | 19 | 0 | GSD security auditor |

## Outstanding Evidence

- Hosted `build-and-style` must pass on the reviewed head or verified PR merge mapping before merge.
- Private B8 remains incomplete until its authorized input and scanner are available.
- Hosted AMD64 DCB runtime verification belongs to Phase 7. Real authentication is deferred to v2 planning.

## Sign-Off

- [x] Each modeled threat has a verified disposition.
- [x] Zero modeled threats remain open.
- [x] Evidence boundaries are recorded.

**Approval** verified for the local implementation on 2026-11-25.
