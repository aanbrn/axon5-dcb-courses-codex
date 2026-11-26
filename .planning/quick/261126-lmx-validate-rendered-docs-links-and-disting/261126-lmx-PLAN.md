---
phase: quick-261126-lmx
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified:
  - docs-site/package.json
  - docs-site/package-lock.json
  - docs-site/verify-site.mjs
  - docs-site/test/site.test.mjs
  - docs-site/eleventy.config.mjs
  - web/test/site-smoke.mjs
autonomous: true
requirements: [FND-06, DOC-06]
estimate:
  tokens: 15000
  raw_tokens: 15000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - Both root and prefixed Eleventy builds reject a missing HTML or Markdown destination and a missing fragment, and publish the valid controls.
    - The public tree contains exactly the nine approved files and rejects private fixture names and bytes.
    - Each published article gives every scrollable table and code sample a distinct, contextual landmark name. Readers can reach the regions by keyboard and scroll overflowing content.
  artifacts:
    - path: docs-site/verify-site.mjs
      provides: Rendered link and fragment validation using parsed attributes
    - path: docs-site/eleventy.config.mjs
      provides: Contextual accessible names for Markdown tables and code fences
    - path: docs-site/test/site.test.mjs
      provides: Root and prefixed build regressions and per-article landmark coverage
    - path: web/test/site-smoke.mjs
      provides: Chromium accessible-name, focus and horizontal-scroll evidence
  key_links:
    - from: docs-site/eleventy.config.mjs
      to: docs-site/verify-site.mjs
      via: The eleventy.after filesystem hook calls verifyPublication using the active path prefix.
    - from: web/test/site-smoke.mjs
      to: docs-site/eleventy.config.mjs
      via: Playwright visits the rendered articles and selects named region landmarks.
---

<objective>
Close WR-04 and WR-03 from the Phase 02 maturity review. Readers should reach valid local links under either deployment base and distinguish command samples from the article's landmark list.
</objective>

<context>
@.planning/quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md
@.planning/phases/02-build-and-ui-foundations/02-CONTEXT.md
@docs-site/build.gradle.kts
@docs/quick-start.md
@docs/maintainer-guide.md
@docs/feasibility/phase-01.md

Dependency decision for WR-04. The installed Eleventy graph includes posthtml-parser 0.11.0, which requires htmlparser2 ^7.1.1 and resolves to 7.2.0. Its HTML-mode Parser already handles the required attribute syntax and entity decoding. A local probe with 7.2.0 recognized mixed-case names, whitespace around equals, unquoted attributes and a decoded named entity, and ignored tag-shaped script text and comments. The npm registry lists 12.0.0 as latest. It falls outside the renderer's dependency range and introduces another parser generation with newer transitive majors. Promote the tested 7.2.0 instance to a directly owned docs build dependency so clean installations can resolve the verifier import independently of npm hoisting. [Upstream parser API](https://github.com/fb55/htmlparser2#usage) · [Publisher releases](https://github.com/fb55/htmlparser2/releases) · [Registry history](https://www.npmjs.com/package/htmlparser2?activeTab=versions)
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Reject broken rendered destinations and fragments under both deployment bases</name>
  <files>docs-site/test/site.test.mjs, docs-site/verify-site.mjs, docs-site/package.json, docs-site/package-lock.json</files>
  <behavior>At / and /courses/, exercise independent failing staged Markdown fixtures for a raw anchor with whitespace around equals targeting a missing article, a raw src targeting a missing asset, an ordinary Markdown link targeting a missing article, and an existing destination with a missing fragment. Check the build exit and the offending destination or fragment in its diagnostic. A positive fixture links to actual files, a decoded element ID and a legacy named anchor. A name on a non-anchor element cannot satisfy a fragment. Include a quoted, an unquoted and a mixed-case attribute, a character reference, and tag-shaped text in a comment or escaped code. Use base-relative paths that keep each fixture in scope. Observe the root raw-anchor regression before changing the verifier.</behavior>
  <action>Extend the existing variant helper's tests against disposable copies of staged articles. Give each negative control its own build so an earlier failure cannot mask the others. Declare htmlparser2 exactly 7.2.0 in docs-site devDependencies and regenerate the npm-owned lock with the docs project's managed Node and npm 12.2.3 using npm install --package-lock-only --ignore-scripts --no-audit --no-fund. Inspect the diff for the direct owner and existing integrity. In verifyPublication replace the tag regex, attribute regex and manual entity decoder with the public Parser opening-tag callback in HTML mode. Parse each rendered page once, collecting href and src and a target set containing id on elements and name on anchors. Resolve the collected links after indexing all pages. Retain URL resolution, external HTTP(S) handling without network requests, deployment-base containment, destination and fragment diagnostics, the nine-file allowlist, and checks on empty files, excluded names and bytes. Keep launch URL policy and canonical staging per D-09, D-10 and D-11.</action>
  <verify><automated>./gradlew --console=plain :docs-site:docsCheck</automated></verify>
  <done>Each independent broken case fails for the expected reason under both bases. The valid builds pass with all nine approved public artifacts, and the existing contamination controls still detect private output.</done>
</task>

<task type="auto" tdd="true">
  <name>Distinguish repeated code and table landmarks in every article</name>
  <files>docs-site/eleventy.config.mjs, docs-site/test/site.test.mjs, web/test/site-smoke.mjs</files>
  <behavior>Read every published article in the rendered output, establish that each code fence and table has a focusable region, and require a meaningful, nonempty name unique within that article. Assert that the three Start the shell steps identify starting the BFF, web app and documentation. Cover the repeated Setup and diagnostics and Reproduce the proof blocks and at least one table. A repeated heading or an absent caption must still yield stable distinct names. Observe the existing duplicates before modifying the renderer.</behavior>
  <action>Extend the existing markdown-it article_accessibility rule and scrollRegion renderer. Keep the kind and section context, use a concise available step description or caption when it identifies the operation, and disambiguate repeated unlabeled blocks with a deterministic per-kind, per-section ordinal. Use the existing heading IDs to distinguish repeated section headings if labels collide. Derive plain text from inline content and escape the final label once. Preserve heading fragments and visible article text, region roles, tab stops and existing overflow styling. In the documentation-specific portion of the existing Chromium siteSmoke, check exact accessible names on the generated pages, including the three quick-start steps. Replace the report's first-match locator with an exact unique name. Check the named article regions are keyboard reachable in document order, verify visible focus, and press ArrowRight on overflowing regions at the existing narrow viewport. Retain the skip-link and page-width assertions. Keep the existing live server and shell test setup.</action>
  <verify><automated>./gradlew --console=plain :docs-site:docsCheck :web:siteSmoke</automated></verify>
  <done>Quick start, the feasibility report and the maintainer guide all pass the per-article checks. Chromium resolves the intended samples by accessible name and demonstrates keyboard focus and horizontal scrolling with the page still fitting its viewport.</done>
</task>

</tasks>

<threat_model>

| Threat ID | Boundary | Category | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-lmx-01 | Rendered markup to public output | Tampering | medium | mitigate | Parse real elements and verify local destinations at both deployment bases. |
| T-lmx-02 | Staged files to publishable tree | Information disclosure | medium | mitigate | Retain the nine-file allowlist and exercise synthetic private filename and byte controls. |
| T-lmx-SC | npm registry to docs build | Tampering | low | mitigate | Reuse the reviewed lock entry and integrity, declare the exact direct owner, and run managed npm ci with scripts disabled through Gradle. |

</threat_model>

<verification>
Run both task verification commands from the checkout root. Preserve the successful launch, canonical report and private-fixture tests. Record the actionable root regression, landmark name examples and Chromium result in the quick summary.
</verification>

<success_criteria>
WR-04 is covered by the two-base valid and invalid publication matrix. WR-03 is covered by article-wide rendered assertions and real keyboard behavior in the existing Chromium smoke suite.
</success_criteria>

<output>
Create .planning/quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md after execution.
</output>
