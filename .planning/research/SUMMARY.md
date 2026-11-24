# Project Research Summary

**Project:** Axon 5 DCB Courses

**Researched:** 2026-11-24

**Overall confidence:** Medium until the Phase 1 compatibility probe succeeds.

## Executive Summary

Use a single DCB write service for decisions that span students, courses, and name claims. Separate projections, event-driven automation, and the REST BFF by responsibility. The highest-risk dependency is the exact Axon Framework, connector, Spring Boot, and Axon Server tuple that supports tagged conditional appends and cross-process routing in the intended local setup. Prove it on a clean database and DCB context before selecting version pins or implementing business features.

## Key Findings

- **Stack.** Retain the brief’s Kotlin, Spring Boot, Axon Server, and React/TypeScript direction. Verify connector distribution and terms, the shared TypeID format, JUnit/Kotest/fixtures, representative KDoc, and the Gradle-to-Paketo frontend build path before pinning. [Stack research](STACK.md)
- **Features.** Enrollment, withdrawals, course administration, student registration, and live views establish a working example. The concurrent last seat, name reuse, transfer, queue promotion, schedule overlap, and exact decision history demonstrate how criteria vary with each operation. [Feature research](FEATURES.md)
- **Architecture.** Axon Server routes commands and queries and stores committed events. Projection processing serves reads and updates. Automation sends promotion commands through the same decision path as a direct request. [Architecture research](ARCHITECTURE.md)
- **Pitfalls.** An incomplete criteria set, uncontrolled automation replay, an incorrect subscription lifecycle, and evidence reconstructed after the fact can each undermine the demo. Verify the real boundaries in integration tests and in the teaching UI. [Pitfall research](PITFALLS.md)

## Implications for Roadmap

1. **Axon Server feasibility and build foundation.** Reconcile the supplied Phase 1 references, review support and terms, and execute a reproducible compatibility probe before committing a matrix. Establish tooling ownership, shared test conventions, and buildpack viability.
2. **UI foundation and service interfaces.** Set the design contract, FSD boundaries, Storybook and accessibility workflow, OpenAPI client graph, and subscription transport.
3. **Core enrollment.** Deliver course and student management, subscriptions and withdrawals, concurrency invariants, live views, and the first complete browser workflow.
4. **Cross-course and name decisions.** Add unique naming and atomic transfer with criteria covering every affected claim and course.
5. **Scheduling and waitlist automation.** Settle policy for overlaps and ineligible queue entries, then exercise promotion, retry, and concurrent changes across services.
6. **DCB teaching experience.** Build the event and boundary inspector and the last-seat demonstration on the recorded evidence. Run load and UI review against the showcase.
7. **Local operations and release evidence.** Verify full Compose operation, local observability, hosted CI and scans, release automation, and the reader-facing documentation and comparative examples.

The ordering is a proposal. Keep contracts, tests, accessibility, documentation, and CI checks growing alongside the features that need them. Further phase research is especially useful for connector licensing and bootstrap, idempotent cross-service automation, and the representation of actual command history.

## Sources

- [Axon Framework and Axoniq Framework comparison](https://docs.axoniq.io/axon-framework-reference/5.4/framework-comparison/)
- [Axon Framework event store internals](https://docs.axoniq.io/axon-framework-reference/5.1/events/event-store-internals/)
- [DCB course subscriptions example](https://dcb.events/examples/course-subscriptions/)
- [Axon Server contexts](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/administration/multi-context/)
- [Paketo Web Servers](https://paketo.io/docs/howto/web-servers/)

---

*Ready for roadmap planning. Runtime compatibility and selected versions are Phase 1 deliverables.*
