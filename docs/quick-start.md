---
title: Quick start
layout: page.11ty.js
---

# Quick start

Use Eclipse Temurin 25 to launch Gradle. The wrapper selects Gradle, and the build provisions Node and npm.

From the repository root, run these commands in separate terminals:

```sh
./gradlew :bff:bootRun --args='--server.address=127.0.0.1'
./gradlew :web:dev
./gradlew :docs-site:serve
```

Open the [demo](http://127.0.0.1:5173/) and the [documentation](http://127.0.0.1:8081/).
