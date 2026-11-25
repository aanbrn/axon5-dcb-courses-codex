# Phase 2: Build and UI Foundations - Discussion Log

The [phase context](02-CONTEXT.md) records the decisions for research and planning. This log preserves the options considered.

**Date:** 2026-11-25

## First BFF scenario

### What should the React shell load through the generated client?

Options considered

- Demo role directory
- Demo information with frontend-defined roles

**Decision.** Load the administrator and multiple demo students from the BFF through the generated TypeScript client and populate the role switcher. If a later version introduces login, use a signed cookie for the session.

### What should the shell show when loading demo roles fails?

Options considered

- Keep the shell usable and show an inline retry
- Show a separate retry screen

**Decision.** Keep the shell and documentation links available. Show the error and a retry action next to the role switcher.

### Where should the BFF API contract be authored?

Options considered

- Kotlin BFF controllers and models with generated OpenAPI
- A checked-in OpenAPI specification with contract conformance tests

**Decision.** Use contract-first OpenAPI in the BFF module. Gradle generates the TypeScript client from the checked-in specification without starting the BFF. Tests verify the HTTP implementation against the contract.

### What belongs in the first published OpenAPI contract?

Options considered

- The implemented demo role operation
- The implemented operation plus separately maintained Phase 3 drafts

**Decision.** Publish only the implemented demo role directory operation. Document how feature slices extend the contract and add browser command, read, and subscription operations as they are implemented.

## Demo role switcher

### Which role should the demo use on first visit?

Options considered

- Administrator
- Demo student
- Explicit selection

**Decision.** Default to the administrator, matching the later enrollment walkthrough that starts with course creation and student registration.

### How long should the selected role persist?

Options considered

- Tab lifetime
- Across visits
- Until reload

**Decision.** Keep the selection scoped to the browser tab and preserve it on reload. Allow different roles to be active in separate tabs.

### How should the initial demo students be presented?

Options considered

- Two named students
- Student A and Student B

**Decision.** Use two named demo students and keep their names consistent across the application, quick start, and examples.

### What should happen when a successful BFF response omits the stored student?

Options considered

- Fall back to administrator with a notice
- Require a new selection

**Decision.** Select the administrator and notify the reader that the previous student is unavailable.

## Documentation entry point

### What should the documentation home page lead with in Phase 2?

Options considered

- Launch the demo
- Introduce DCB

**Decision.** Lead with launching the React demo shell and provide a link to the Phase 1 DCB feasibility report.

### Where should the Phase 1 report link lead?

Options considered

- Documentation site report page
- Repository report link

**Decision.** Render the report as a page in the documentation site using its existing repository Markdown source.

### Where should maintainer instructions be available?

Options considered

- Maintainer Guide in the site
- Repository instructions linked from the site

**Decision.** Include a Maintainer Guide in the site for tool inventory, doctor, and dependency maintenance and advisory procedures. Keep private inputs and results local.

### How should readers open the demo from the documentation site?

Options considered

- Open demo when configured with a Quick Start fallback
- Always route through Quick Start

**Decision.** Show an Open demo action when the app URL is configured. Route readers to local launch instructions otherwise.

## Local checks

### What files should the pre-commit hook check?

Options considered

- Staged files
- Whole repository

**Decision.** Check the staged content. CI applies the same rules to the whole repository.

### How should the hook handle formatting changes?

Options considered

- Include formatting in the current commit
- Format and stop for the author to stage the changes

**Decision.** Format staged content and include the formatting in the current commit. Preserve unstaged edits.

### What should doctor show by default?

Options considered

- One report with required and additional checks
- Build prerequisites by default with an additional mode

**Decision.** Show required and additional checks in one report. Distinguish prerequisites for a regular build from Docker checks and image packaging tools.

### What should Phase 2 GitHub Actions run?

Options considered

- Style and clean build
- Style checks only

**Decision.** Run style checks and a clean ./gradlew build on PRs without Docker.

### When should the first hosted AMD64 DCB runtime check run?

Options considered

- Phase 7 using equivalent application coverage when available
- Separate Phase 2 :probe run

**Decision.** Schedule the check in Phase 7. Use the application suites if they provide the required evidence, with :probe as a fallback. This supersedes the timing in Phase 1 D-05.

## Follow-up

The code-first question prompted a review of Springdoc's build-time startup behavior. The selected contract-first approach keeps client generation independent of a running BFF.

The timing of hosted AMD64 verification came up after the initial review. The Phase 1 timing referred to the start of hosted CI and the roadmap placed the runtime evidence in Phase 7. The discussion confirmed Phase 7 as the first hosted AMD64 DCB runtime check after the addition of build-only CI in Phase 2.

## Research and design discretion

Phase research will select the client generator and docs engine. The UI-SPEC will define the screen and interaction details.
