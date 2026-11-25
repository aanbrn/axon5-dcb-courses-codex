---
phase: "01"
slug: axon-server-and-toolchain-feasibility
status: verified
threats_open: 0
asvs_level: 1
created: "2026-11-25"
---

# Phase 01 Security

This review covers the planned threat register for the local feasibility probe. The evidence is acceptance run `acceptance-nvahwpkb` and the retained verification of its published report. [Feasibility record](../../../docs/feasibility/phase-01.md)

## Trust Boundaries

| Boundary | Description | Data crossing |
| --- | --- | --- |
| Publisher and registry to build | Obtain selected tool, Maven, npm, and immutable OCI inputs. | Public releases, checksums, manifests, resolved coordinates, and package integrity hashes. |
| Host JVMs to local Docker and Axon Server | Start clean scoped fixtures and exchange DCB commands, events, and queries. | Test-only typed messages and tagged events over loopback. |
| Buildpack to local HTTP receiver | Package the staged static fixture and verify it in a native container. | Allowlisted staged HTML and response bytes. |
| Local evidence to published report | Validate the output before including bounded observations and public references in the repository. | Run identities, measured versions, digests, outcomes, and public terms. |

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| T-01-01 | Tampering | Wrapper and server image | high | mitigate | Wrapper JAR SHA-256 matches the publisher. Distribution checksum, raw index and child/config bytes, and the running ARM64 config identity are verified. | closed |
| T-01-02 | Spoofing and information disclosure | Standalone and role startup | high | mitigate | Integration fixture uses a fresh container without mounts, explicit DCB context and loopback ports, empty role homes and an allowlisted startup environment. The run observes unregistered mode. | closed |
| T-01-03 | Spoofing and tampering | DCB conflict and subscription | high | mitigate | Separate JVMs register with Axon Server. The stale append returns the explicit conflict, only the winner is read under both tags, and the existing subscription receives the correlated projection update. | closed |
| T-01-04 | Denial of service | Subscription, processes and container | medium | mitigate | Native success and forced failure cases assert bounded cancellation, child exits, owned container removal, and survival of a separate network. | closed |
| T-01-05 | Tampering and information disclosure | Paketo staging and serving | high | mitigate | Staging allows one directory and one HTML file. Both distinct native images serve the exact expected bytes through loopback. | closed |
| T-01-06 | Denial of service | Pack and native containers | medium | mitigate | The image producer applies readiness bounds, verifies container image identities, and removes only scoped containers, images and build caches. | closed |
| T-01-07 | Tampering | TypeID exchange and test discovery | medium | mitigate | Named Jupiter cases execute, both independent language outputs validate prefix and bytes, and stale or mismatched output fails verification. | closed |
| T-01-08 | Repudiation and tampering | Evidence and platform conclusions | high | mitigate | The report checker binds the actual run and JUnit evidence to immutable inputs and outputs. Accepted AMD64 scope is registry metadata. The verifier rejects mismatched evidence and generic repeated failure signatures. | closed |
| T-01-09 | Information disclosure | Public report and guide | high | mitigate | Public artifacts contain bounded results and source links. Raw captures, inventories, and credential context remain local. | closed |
| T-01-SC | Tampering | External dependencies, tools, and images | high | mitigate | Publisher coordinates and image checksums were matched against the resolved inputs. Scoped constraints move both affected Guava graphs to `33.8.0` with unchanged control graphs and passing applicable checks. npm locks and actual executables were verified. | closed |

## Accepted Risks Log

The isolated `probe/typeid` fixture retains the Moderate `GHSA-w5hq-g745-h8pq` advisory for `uuid@10.0.0`. The measured call surfaces use TypeID encoding and decoding and the installed module imports `stringify` and `v7`. The advisory covers `v3`, `v5`, and `v6` with caller-provided output buffers. The build maintainer reviews the fixture by 2026-12-02 and repeats verification when a publisher release selects a fixed UUID version or the fixture call surface changes. The application dependency choice remains open. [uuid advisory](https://github.com/advisories/GHSA-w5hq-g745-h8pq)

The private JVM advisory procedure remains incomplete. Hosted scanning, optional Platform connectivity, and hosted AMD64 runtime are separate roadmap work. [Project dependency policy](../../PROJECT.md)

## Security Audit Trail

| Audit date | Threats total | Closed | Open at or above high | Run by |
| --- | --- | --- | --- | --- |
| 2026-11-25 | 10 | 10 | 0 | GSD Phase 01 security review |

## Sign-Off

- [x] Every planned threat has a verified mitigation or a recorded scope.
- [x] The isolated Moderate advisory and incomplete private review are disclosed.
- [x] The modeled high and critical threshold is clear.
