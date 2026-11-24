# Feature Research

**Project:** Axon 5 DCB Courses

**Date:** 2026-11-24

## Baseline Workflows

| Workflow | Observable result | Dependencies |
| --- | --- | --- |
| Course and student administration | An admin creates and renames a course, changes capacity, defines its schedule, and registers students. | Course and student identities and a live catalog. |
| Enroll and withdraw | A selected student sees current subscriptions and receives a result when applying or withdrawing. | Course and student history, DCB decisions, and live query views. |
| Live status | The catalog and student views update as projections process committed events. | QueryBus, subscription queries, and a browser-facing stream. |
| Demo roles | A reader can switch between admin and individual students. | A frontend identity selector and clear demo context. |

## Teaching Scenarios Included in v1

| Scenario | Demonstration | Effort and dependency |
| --- | --- | --- |
| Last seat and subscription limit | Race several students for the last seat and several courses for one student’s remaining allowance. Show the final committed state alongside attempt outcomes. | High. Requires comparable concurrent requests and an observable final state. |
| Unique course name | Race two claims for the same name and show that a successful rename releases the former name. | Medium. Requires identity, name normalization policy, and writes spanning the old and new name claims. |
| Atomic transfer | Move the same student across two courses in one decision. A rejected move preserves the original enrollment. | High. Requires the enrollment baseline and the applicable policy checks. |
| Waiting list | A full course accepts a queue request and promotes the next student when a seat opens. | High. Requires a vacancy signal and event-driven automation that rechecks live invariants. |
| Overlapping courses | Demonstrate an allowed enrollment and a rejection caused by conflicting schedule slots. | High. Requires a defined overlap rule and a criteria design for schedules consulted by the decision. |
| Event and boundary inspection | Browse event tags and see the historical events the selected command read, together with the criteria used to make that decision. | High. Requires capture at the command boundary and stable event references. |

The DCB examples describe the multi-entity enrollment and uniqueness patterns separately. Their application to the waitlist, transfer, schedule, and browser demos is specific to this project. [Course subscriptions example](https://dcb.events/examples/course-subscriptions/) · [Unique username example](https://dcb.events/examples/unique-username/)

## Scope Boundaries

V2 carries real authentication and authorization. Keep the aggregate comparison in diagrams and snippets. The v1 local deployment uses Docker Compose, and one command service owns all course and student writes. Leave course-name normalization, waitlist eligibility after a student’s state changes, schedule semantics, and the exact demo race workload to phase discussion where the team can record and verify the chosen behavior.
