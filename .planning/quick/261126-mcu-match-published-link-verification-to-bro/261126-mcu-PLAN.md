---
phase: quick-261126-mcu
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - docs-site/verify-site.mjs
  - docs-site/test/site.test.mjs
  - docs/maintainer-guide.md
autonomous: true
requirements: [FND-06, DOC-06]
estimate:
  tokens: 16000
  raw_tokens: 16000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - At / and /courses/, an active base element with href fails the publication build and identifies the source page.
    - Links can target a template element's own ID and live elements after a template. Targets existing exclusively inside template content fail, and inert links do not become publication links.
    - A local pathname containing a percent-encoded slash fails publication at both bases. Encoded fragment IDs and ordinary links with queries keep working.
    - Both valid builds publish precisely the existing nine nonempty files and retain the canonical report and private fixture checks.
  artifacts:
    - path: docs-site/verify-site.mjs
      provides: Active-document indexing and local path validation
    - path: docs-site/test/site.test.mjs
      provides: Independent Eleventy rejection fixtures and passing controls at each deployment base
    - path: docs/maintainer-guide.md
      provides: Authoring rules for links in published documentation
  key_links:
    - from: docs-site/eleventy.config.mjs
      to: docs-site/verify-site.mjs
      via: The existing eleventy.after hook verifies the finished filesystem output with its deployment base.
    - from: docs-site/test/site.test.mjs
      to: docs-site/verify-site.mjs
      via: The variant helper exercises the hook on fresh builds of staged Markdown and raw HTML.
---

<objective>
Close three reproduced WR-04 false successes in the Phase 02 publication check. A reader following a verified internal link must reach a published route and, when supplied, a fragment in the active document. Use the existing htmlparser2 dependency and public output inventory. Apply both policies at the normal Eleventy publication entry point.
</objective>

<execution_context>
@.codex/gsd-core/workflows/execute-plan.md
@.codex/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-build-and-ui-foundations/02-CONTEXT.md
@.planning/quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md
@docs-site/verify-site.mjs
@docs-site/test/site.test.mjs
@docs-site/serve.mjs
@docs-site/eleventy.config.mjs
@docs/maintainer-guide.md

The independent reviewer reproduced successful builds for all three invalid fixtures at both deployment bases. The document base changes the reader's relative destination. A template's content has its own document fragment. The documented preview performs an exact route lookup on the request path before the query string, while the verifier decodes the pathname before matching filenames. Use these observations to design the checks. Record local build, browser and HTTP observations separately with their source and base. A hosted deployment requires its own evidence.
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Reject active base overrides and index only active document targets</name>
  <files>docs-site/test/site.test.mjs, docs-site/verify-site.mjs</files>
  <behavior>For each base, an active base href in Quick start fails, a live link to a fragment found only inside a template fails, and valid live targets together with inert markup build successfully.</behavior>
  <action>In the existing two-base test loop use variant(t, { base }) and append fixtures to the temporary quick-start.md. Give each cause of rejection its own build. For the base case insert an active base whose href is ../feasibility/phase-01/ and a real anchor whose href is ../maintainer-guide/. The fixture's document-relative link would otherwise pass and its base-relative destination is the absent feasibility/maintainer-guide/ route. For the fragment case link to #template-only from outside two nested template elements with the sole matching id inside the inner template. Assert exit 1 and a diagnostic naming quick-start/index.html and the offending base href or missing fragment. First run docsCheck against the current verifier and capture the named unexpected zero exits at both bases. Implement the active-document traversal using the existing htmlparser2 Parser callbacks. Track template nesting, index each active template element's own attributes, skip descendants including id, anchor name, links and base elements, and resume indexing its live siblings. Reject any active base element carrying href, including an empty value, with a specific diagnostic. Pass the rendered source name into indexing if needed. Add a successful fixture with a link to the template element's own ID, a live target after nested templates, and inert links and base markup that would otherwise fail. Preserve ordinary parser handling of HTML attributes, entities, comments and escaped examples. Keep indexing all rendered pages before checking cross-page fragments.</action>
  <verify><automated>mise exec java -- ./gradlew --console=plain :docs-site:docsCheck</automated></verify>
  <done>The new negative cases fail for the intended reasons at each base and the positive template controls and existing parser controls pass.</done>
</task>

<task type="auto" tdd="true">
  <name>Reject percent-encoded path separators and document the accepted link forms</name>
  <files>docs-site/test/site.test.mjs, docs-site/verify-site.mjs, docs/maintainer-guide.md</files>
  <behavior>At each base, ../feasibility%2Fphase-01/ and its lowercase %2f equivalent each fail. A literal slash reaches the same published article. An encoded slash in a query or in a fragment with a matching live ID remains valid.</behavior>
  <action>Use independent rendered builds for the uppercase and lowercase negative fixtures through the same variant helper. Assert exit 1 and a path-specific diagnostic containing the source name and offending link. Record RED before implementing the check. On internal links, inspect the resolved URL pathname for a case-insensitive percent-encoded forward slash before converting it to a public filename. Preserve the deployment-prefix boundary, existing absolute HTTP(S) behavior, query handling and separate decoding of the fragment. Extend the green controls with a canonical article path, a query containing %2F, a fragment containing %2F with a matching active ID containing a slash, and the existing percent-encoded UTF-8 fragment. In the guide's Documentation build section briefly describe document-relative links, the active base href prohibition, literal path separators and active fragment targets. Use inline code for markup examples. Retain launch selection, canonical source staging and private input isolation per D-09 through D-11. Check the sorted regular-file list of both valid outputs against an explicit test expectation independent of publicFiles: index.html, quick-start/index.html, feasibility/phase-01/index.html, maintainer-guide/index.html, site.css, fonts/geist-latin-wght-normal.woff2, fonts/geist-mono-latin-wght-normal.woff2, fonts/geist-LICENSE.txt and fonts/geist-mono-LICENSE.txt. Retain all existing exact-file, nonempty-file, excluded-name and excluded-byte gates.</action>
  <verify><automated>mise exec java -- ./gradlew --console=plain :docs-site:docsCheck</automated></verify>
  <done>Both builds reject the encoded path forms, publish the valid controls and contain the same nine expected files. The guide explains the authoring rules and existing tests for launch policy, canonical bytes and private fixtures pass.</done>
</task>

</tasks>

<threat_model>

| Threat ID | Boundary | Category | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-mcu-01 | Raw article HTML to active navigation | Tampering | medium | mitigate | Reject active base overrides and index the active document outside template content. |
| T-mcu-02 | Internal URL to public route | Tampering | medium | mitigate | Reject encoded forward slashes in local URL paths and retain prefix containment. |
| T-mcu-03 | Staged files to published site | Information disclosure | medium | mitigate | Check the exact nine outputs and retain excluded filename and byte controls. |
| T-mcu-SC | Build dependencies | Tampering | low | accept | The existing directly declared parser and lockfile cover this change. |

</threat_model>

<verification>
Run the full docsCheck task at the default base, then run `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck -PdocsBase=/courses/`. Each suite also creates isolated Eleventy variants under both bases. Capture test outcomes and actual diagnostics. Treat the reproduced encoded-route 404 as local preview evidence and the static fixture assertions as publication evidence. Attribute prior browser observations to the review and record any new browser or hosted measurements only when actually performed.
</verification>

<success_criteria>
The two publication bases reject all three reproduced false successes, retain valid navigation and publish exactly nine files. The change uses the existing parser, fixtures and Gradle entry point.
</success_criteria>

<output>
Create `.planning/quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md` after execution with the named RED and GREEN outcomes, tested bases and evidence provenance.
</output>
