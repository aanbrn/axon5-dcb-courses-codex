---
phase: quick-261126-fxn
plan: "01"
type: execute
wave: 1
depends_on: []
files_modified: [mise.toml, .github/workflows/build.yml, tools/check_pr_workflow.py, tools/doctor.py, docs/maintainer-guide.md]
autonomous: true
requirements: [FND-02, QA-08]
must_haves:
  truths:
    - Developers and the PR style job can run the same Python patch version.
    - Both doctor modes identify the configured pin and fail on an interpreter mismatch.
    - The PR job checks its workflows with actionlint and ShellCheck at the versions selected by mise.
    - Both doctor modes report the presence of GSD for Codex as information.
  artifacts:
    - path: mise.toml
      provides: Authoritative Python pin
  key_links:
    - from: tools/doctor.py
      to: mise.toml
      via: Comparison of the running interpreter with tools.python
    - from: .github/workflows/build.yml
      to: mise.toml
      via: Mise Action installation and Gradle styleCheck environment
---

<objective>
Use the Python version selected by mise for repository tooling and the PR style job. Run pinned actionlint and ShellCheck in the existing PR job. Python tooling uses the standard library.
</objective>

<tasks>
<task type="tracer" tdd="true">
  <name>Pin Python and run workflow lint in the PR style job</name>
  <files>mise.toml, .github/workflows/build.yml, tools/check_pr_workflow.py, tools/doctor.py, docs/maintainer-guide.md</files>
  <behavior>Cover a different patch of the same Python minor in doctor's existing self-tests. Assert a required failure with owner, expected and observed versions, and repair guidance in both bootstrap and Gradle modes. Run the passing path with the configured interpreter.</behavior>
  <action>Pin Python 3.15.2, actionlint 1.7.12 and ShellCheck 0.11.0 under [tools] in mise.toml. Read the mise inventory once in doctor, compare the running Python version with its exact pin, and report exact actionlint and ShellCheck versions from the executables. In build-and-style, add the three tools to MISE_ENABLE_TOOLS and install_args. Log the selected versions and run a workflow lint step with mise exec actionlint shellcheck -- actionlint -shellcheck=shellcheck -pyflakes=, followed by styleCheck with mise exec python ruff taplo. Keep the exact order and commands in tools/check_pr_workflow.py with a negative control for a missing lint step if needed. Preserve the existing action SHAs, permissions, wrapper validation, Java/Node ownership and direct clean Gradle build. Update the maintainer inventory and commands for setup, doctor, local workflow lint, the style check, Python scripts and hook execution through an activated mise environment. Prefix the local Qodana examples with mise exec python --. Scope the changes to the existing local tools and PR job. The standalone probe retains its compatibility contract, and QA-08 still needs hosted evidence.</action>
  <verify>
    <automated>mise exec python -- python3 -c "import platform, sys, tomllib; pin = tomllib.loads(open('mise.toml', encoding='utf-8').read())['tools']['python']; sys.exit(platform.python_version() != pin or pin != '3.15.2')"</automated>
    <automated>mise exec python -- python3 tools/doctor.py --self-test</automated>
    <automated>mise exec python ruff taplo -- python3 tools/style/test_hook.py</automated>
    <automated>mise exec python -- python3 tools/check_pr_workflow.py</automated>
    <automated>mise exec aqua:rhysd/actionlint shellcheck -- actionlint -shellcheck=shellcheck -pyflakes=</automated>
    <automated>mise exec python aqua:rhysd/actionlint shellcheck ruff taplo -- ./gradlew --console=plain styleCheck doctor :docs-site:docsCheck</automated>
  </verify>
  <done>The selected Python, actionlint and ShellCheck report the pinned versions, doctor detects Python patch drift, and the hook fixtures, workflow controls, workflow lint, style, doctor and documentation checks pass.</done>
</task>
</tasks>

<threat_model>
| Threat ID | Category | Component | Severity | Disposition | Mitigation |
| --- | --- | --- | --- | --- | --- |
| T-261126-fxn-01 | Tampering | Interpreter selected by PATH | low | mitigate | Invoke tools through mise and have doctor compare the running interpreter with the tracked pin. |
| T-261126-fxn-02 | Tampering | PR workflow | low | mitigate | Validate the allowed tool list, installation and style invocation with the existing exact workflow guard. |
</threat_model>

## Execution Clarifications

Use the explicit `aqua:rhysd/actionlint` key consistently in mise selection after the short invocation attempted to resolve a different tool key. Report GSD for Codex from the known CLI path in the checkout or Codex configuration. This is informational and does not affect doctor readiness. Both clarifications use the files already owned by the task.

<output>
Record the observed interpreter and local verification results in 261126-fxn-SUMMARY.md.
</output>
