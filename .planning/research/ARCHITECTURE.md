# Architecture Research

**Project:** Axon 5 DCB Courses

**Date:** 2026-11-24

## Service Responsibilities

| Role | Inputs | Durable state and output |
| --- | --- | --- |
| Command | Commands routed through Axon from the BFF or automation | Reads relevant tagged history, evaluates invariants, and conditionally appends resulting events to Axon Server. |
| Query/projection | Committed events and QueryBus requests | Builds dedicated read models, stores processing progress, and serves initial results and live updates. |
| Automation | Committed events that make a seat available | Tracks its own processing progress and sends promotion commands. The command service decides whether a promotion commits. |
| REST BFF | Browser requests based on the OpenAPI contract | Translates requests to Axon commands and queries and bridges subscription results to the browser. |
| React frontend | User actions and BFF responses | Renders live catalog and student state, queue and decision outcomes, and DCB teaching views. |

Share stable message contracts across roles, and keep service implementations independently testable. One command decision may consult a student, multiple courses, and name claims. Axon’s event criteria and consistency marker provide the documented mechanism for detecting intervening writes that match the relevant history. The project must prove that its actual command handler and append behavior use the intended criteria. [Axon event store internals](https://docs.axoniq.io/axon-framework-reference/5.1/events/event-store-internals/)

## Data Flow to Prove

1. The frontend sends an operation to the BFF through the generated contract. The BFF routes the command to the command service through Axon Server.
2. The command service selects a command-specific history, evaluates the business rule, and commits events only if the append condition still holds. A retry reevaluates against fresh history.
3. The query service consumes committed events, updates its models, and emits subscription updates associated with committed projection changes. The BFF owns the browser stream’s lifetime and reconnection behavior.
4. The automation service reacts to vacancy events and submits an idempotent promotion command with stable correlation. Projection replay and automation resume need separate verification because replay can reconstruct data while automation can cause writes.

For the teaching UI, distinguish the criteria used by the decision from any effective criteria added during append. Capture the stable event references that the command actually consumed and selected decision metadata, then correlate the attempt with the final outcome. Decide how to capture rejections and concurrency conflicts in the teaching phase. A later tag query may include events written after the original attempt. [Axon append and sourcing conditions](https://docs.axoniq.io/axon-framework-reference/5.1/events/event-store-internals/) · [Query gateway subscription lifecycle](https://docs.axoniq.io/axon-framework-reference/5.0/queries/infrastructure/)

## Build Order

Prove the compatibility tuple and transport with a narrow sample, then establish the UI and OpenAPI build path before the business slices. Ship baseline enrollment with live reads first. Add uniqueness and atomic transfer, and incorporate waitlist and schedule interactions once the baseline behavior is observable. Build the teaching views using the actual command evidence. Keep telemetry, CI, and documentation incrementally verifiable, then run the full Compose and release review against the combined system.
