---
phase: quick-261126-fhh
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified: [mise.toml, docs/maintainer-guide.md]
autonomous: true
requirements: [FND-02]
must_haves:
  truths:
    - Developers can invoke the repository's Temurin JDK and Node.js with mise.
  artifacts:
    - path: mise.toml
      provides: Project settings for idiomatic runtime files and independent CLI pins
    - path: docs/maintainer-guide.md
      provides: Optional developer shell setup
  key_links:
    - from: mise.toml
      to: .java-version
      via: Java idiomatic file detection and Temurin shorthand
    - from: mise.toml
      to: .nvmrc
      via: Node idiomatic file detection
---

<objective>
Make mise select the repository's Temurin JDK and Node.js for an optional developer shell, and explain where maintainers change each version.
</objective>

<context>
@.planning/PROJECT.md
@.java-version
@.nvmrc
@mise.toml
@docs/maintainer-guide.md
</context>

<tasks>
<task type="tracer">
  <name>Read the canonical runtime files and document shell setup</name>
  <files>mise.toml, docs/maintainer-guide.md</files>
  <action>Add a short English header to mise.toml explaining that it owns the independent Pack, Ruff and Taplo pins and reads the Java and Node versions from .java-version and .nvmrc. Keep all three CLI pins. Under [settings], set idiomatic_version_file_enable_tools to java and node, java.shorthand_vendor to temurin, and idiomatic_version_file_disable_files to java:.sdkmanrc, node:.node-version and node:package.json. Explain why the alternative inputs are excluded. Under “Setup and diagnostics” in the maintainer guide, show how to install and invoke the optional shell runtimes through mise, including how to inspect the selected files. Preserve the explicit CI and regular-build selections for Temurin, Gradle-managed Node/npm and the independent style tools.</action>
  <verify>
    <automated>mise ls --current</automated>
    <automated>mise exec java node -- java -XshowSettings:properties -version</automated>
    <automated>mise exec java node -- node -p "process.versions.node"</automated>
    <automated>mise exec ruff taplo -- ./gradlew --no-daemon --console=plain styleCheck doctor</automated>
    <automated>./gradlew --no-daemon --console=plain :docs-site:docsCheck</automated>
  </verify>
  <done>The mise listing attributes Java to .java-version and Node to .nvmrc. The running JVM reports Eclipse Adoptium and the feature in .java-version. The running Node version equals .nvmrc. The style, doctor and documentation checks pass. Use checkout-scoped trust if mise requests it and leave global settings intact.</done>
</task>
</tasks>

<threat_model>
| Threat ID | Category | Component | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-261126-fhh-01 | Tampering | Local runtime selection | Low | mitigate | Restrict idiomatic inputs to the two canonical files. Verify their paths and both running versions. |
</threat_model>

<output>
Record the selected runtime sources, observed versions and check results in 261126-fhh-SUMMARY.md in this quick task directory.
</output>
