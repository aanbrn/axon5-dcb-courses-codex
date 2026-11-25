---
phase: 01-axon-server-and-toolchain-feasibility
plan: "03"
subsystem: build
tags: [gradle, node, npm, paketo, arm64, evidence]
requires:
  - phase: "01-02"
    provides: "A native Axon DCB proof and the secondary evidence verifier."
provides:
  - "A deterministic, dependency-free HTML fixture with a verified npm lockfile."
  - "An isolated Gradle Node build and a scoped npm entry point for the TypeID exchange."
  - "Two native Paketo HTTP responses that match their distinct staged inputs byte-for-byte."
affects: [01-04, 01-05, 02, 05]
actuals:
  tokens: 8054
  tasks: 3
  commits: 3
commits: 3
plan_head_before: 4ec6ba74307dd2cb0fcb8e15e8804f3d638889a4
plan_head_after: 3ac7d2bc41af1007aff7b652e50626180c757284
tech-stack:
  added: [Node 26.13.1, npm 12.2.3, Gradle Node 7.1.0, Pack 0.40.11, Paketo Web Servers 4.16.3]
  patterns: [Isolated npm build, public-only staging, digest-pinned native packaging]
key-files:
  created:
    - .nvmrc
    - mise.toml
    - probe/web/package.json
    - probe/web/package-lock.json
    - probe/web/build.mjs
    - probe/web/settings.gradle.kts
    - probe/web/build.gradle.kts
  modified:
    - gradle/libs.versions.toml
    - probe/build.gradle.kts
key-decisions:
  - "Use Node 26.13.1 and npm 12.2.3 through their separate version owners, with the Gradle Node plugin confined to the nested web build."
  - "Package only the validated staged public tree with the digest-pinned Paketo Jammy builder, run image and Web Servers buildpack."
patterns-established:
  - "Serve independently built marker assets on ephemeral loopback ports and verify the running image identity and response bytes."
  - "Expose scoped npm scripts with declared probe inputs and outputs for cross-language verification."
requirements-completed: [FND-01]
coverage:
  - id: D1
    description: "Clean npm installs preserve the lockfile and repeated inputs produce identical bytes."
    requirement: FND-01
    verification:
      - kind: other
        ref: "python3 probe/verify_secondary.py check frontend-fixture"
        status: pass
    human_judgment: false
  - id: D2
    description: "The isolated Gradle build verifies Node, npm, the lockfile and the staged public tree."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_secondary.py check frontend-assets"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two native Paketo images serve the corresponding staged bytes over HTTP and release probe-owned resources."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_secondary.py check frontend-image"
        status: pass
    human_judgment: false
duration: 393min
completed: 2026-11-25
status: complete
---

# Phase 01 Plan 03: Static Frontend Packaging Summary

**Two Pack-built Linux/ARM64 images served distinct Gradle-staged HTML documents with HTTP 200 and byte-for-byte agreement.**

## Accomplishments

- The fixture has zero npm dependencies. Two clean builds with the same marker produced identical bytes, and a different marker changed the HTML. The lockfile stayed at SHA-256 `86015f6a4fddc302cefbfbf5c842d1711d3efb3d98dfac3a6878afd1c92e5880`.
- The nested Gradle Node 7.1.0 build verified child executables Node `v26.13.1` and npm `12.2.3` before `npm ci`. The default staged HTML hash was `87d1cd7e7502b9df718f95140c75272c17b1fa3f9102cb84405a58681643a656`. Changing `-PprobeMarker` rebuilt the asset and produced hash `6cda0d8210b77abe0951933038b246d9e3289d6d355970772ae7f8e1270ab014`. The staged tree contained one index document under the public directory.
- The ordinary Gradle build ran its JVM smoke test. `./gradlew --console=plain build --dry-run` showed only the ordinary compile, test, and build graph. The image check and native Axon integration suite are explicit entry points.
- Pack `0.40.11+git-523c9ce.build-7117` used lifecycle `0.21.29` on Linux/ARM64 Docker `29.10.0`. Web Servers `4.16.3` selected the nginx `1.3.8` buildpack with NGINX `1.31.9`. The active buildpacks were CA Certificates, Nginx, and Source Removal. The probe verified each running container's image ID and removed its scoped containers, networks, output tags, and build-cache volumes.

## Reproduction and Evidence

The fresh required Axon proof `core-vn2dqfdj` anchors three `Pass` stages in the generated report at probe/build/reports/feasibility/secondary/frontend.json. Each stage had raw exit `0`. The retained records contain the exact arguments, diagnostics, and hashes of the supporting files. The three frontend commands took about 2, 13 and 133 seconds during the final capture. The plan wall time includes the interval between direct verification and formal evidence collection.

```bash
python3 probe/verify_secondary.py ensure-core
python3 probe/verify_secondary.py run frontend-fixture -- bash -c 'npm --prefix probe/web ci && npm --prefix probe/web run build && node -e "const f=require(\"node:fs\");if(!f.readFileSync(\"probe/web/build/staged/public/index.html\",\"utf8\").includes(\"phase-one-static\"))process.exit(1)" && node probe/web/build.mjs --verify-fixture'
python3 probe/verify_secondary.py run frontend-assets -- ./gradlew --console=plain :probe:frontendAssets --rerun-tasks
python3 probe/verify_secondary.py run frontend-image -- ./gradlew --console=plain :probe:frontendAssets :probe:frontendImageProbe --rerun-tasks
python3 probe/verify_secondary.py check frontend-fixture
python3 probe/verify_secondary.py check frontend-assets
python3 probe/verify_secondary.py check frontend-image
```

Use the Node and npm executables declared by `.nvmrc` and `probe/web/package.json` on `PATH` for the direct fixture command. Gradle provisions them for the other two stages. Pin the Pack executable through `mise.toml` and use a native ARM64 daemon for the image check. [Node.js v26.13.1](https://nodejs.org/en/blog/release/v26.13.1) · [npm CLI v12.2.3](https://github.com/npm/cli/releases/tag/v12.2.3) · [Gradle Node 7.1.0](https://github.com/node-gradle/gradle-node-plugin/releases/tag/7.1.0) · [Pack v0.40.11](https://github.com/buildpacks/pack/releases/tag/v0.40.11)

| Marker | HTTP | Staged and served SHA-256 | Running image ID |
| --- | --- | --- | --- |
| `phase-one-static-first` | 200 | `131c842ebb0e163dd65c83f5b43f13373cc87e2e41774b557a42451c2e1ff41f` | `sha256:066625a50238f95e1948ff1cb5d56cea5a5a5bfaf2f7f3321201b5cf1cd527ed` |
| `phase-one-static-second` | 200 | `a2cd76489a80b83403a85a8924a2153ee66332d55b8c7e52bfd0d56070280bf5` | `sha256:b9ac7d44d757c3b29ad452a971ad094f1fa1fa1aaf97fa3c7ad9ab54a39b6e52` |

| Paketo input | OCI index digest | Linux/ARM64 child | Linux/AMD64 child |
| --- | --- | --- | --- |
| Jammy buildpackless base `0.0.363` | `sha256:5af7e0854783326ba6da9f038b6cb5206a5712478c7ffc096c43b122b94e3ea7` | `sha256:67707cbbb950ebcb578896984e41fb6b90a17b26e482cebbe2f395347a633516` | `sha256:b0c041c3762ab0af72c1df4fb73bd2b53d25853f2a2a23723db4dbf964f81030` |
| Jammy run image | `sha256:82fa301ed3ad37ace7cace269292f14abb7286dfb418f34465975322fd830af2` | `sha256:e4238e2d789e29b4c7ad07f7f79d9a3d7db0511f40fd56f8c986b361622848b2` | `sha256:f3aae54cf111a45a2d63a6a78270a42f31639ae6e9019eecaf0e3f2aa38fa7fc` |
| Web Servers `4.16.3` | `sha256:a01f811143ca2629a1cfb2b053a63de0b845cf6e38d19ca375f2c3d6c62c6e97` | `sha256:d0600f9c22f6fbb9f0900a75cb8667300374d5c3c81f0ba125304f6f4ebe4c73` | `sha256:13da8eb94d36f85bd92fc85502d8790ca0c68d88c35c9257f0ead6f971582e73` |

The registry response digests matched the raw index and child manifest bytes and the child configs. Before packaging, Docker reported each catalogued ARM64 child’s expected config ID. The builder identifies the Jammy run image, which the probe resolves by immutable digest. AMD64 observations are publisher registry metadata. Its runtime verification remains scheduled under D-05. [Jammy buildpackless builder 0.0.363](https://github.com/paketo-buildpacks/builder-jammy-buildpackless-base/releases/tag/v0.0.363) · [Web Servers 4.16.3](https://github.com/paketo-buildpacks/web-servers/releases/tag/v4.16.3) · [Paketo Web Servers guide](https://paketo.io/docs/howto/web-servers/)

## Task Commits

1. `bfb2e63` — Build a deterministic npm fixture.
2. `f160d69` — Isolate npm installation and static staging in Gradle.
3. `3ac7d2b` — Verify native Paketo static serving.

## Deviations from Plan

- **[Rule 1 — Tool compatibility]** npm 12 warns that `manage-package-manager-versions` is no longer recognized. The Gradle task and fixture dropped that setting and preserved direct executable checks in `f160d69`.

## Plan 04 Handoff

Use the same toolchain and `npm ci` implementation for the TypeID exchange:

```bash
./gradlew --console=plain -p probe/web scopedNpmBuild \
  -PprobeNpmDir=probe/typeid -PprobeNpmScript=check-vectors
```

Pass `-PprobeNpmInputs` and `-PprobeNpmOutputs` as comma-separated repository-relative paths under `probe` to model the exchange files. Without explicit outputs, the selected script runs on every invocation. The scoped path was exercised with a separate disposable manifest, lockfile, and declared input and output. FND-01 remains open for the remaining secondary checks and final Phase 01 acceptance.

## Self-Check: PASSED

All nine implementation files exist and all three task commits are reachable. The three stage checks validated the combined frontend report against the fresh native core evidence.
