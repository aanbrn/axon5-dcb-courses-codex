---
title: Quick start
layout: page.11ty.js
---

# Quick start

Clone the [repository](https://github.com/aanbrn/axon5-dcb-courses-codex) and use Eclipse Temurin 25 to launch Gradle. The wrapper selects Gradle, and the build provisions the pinned Node and npm releases. The shell and role directory run without Docker or Axon Server.

## Start the shell

From the repository root, run one command per terminal.

1. Start the BFF at `http://127.0.0.1:8080`. Check its [OpenAPI document](http://127.0.0.1:8080/openapi.json) once it starts.

   ```sh
   ./gradlew :bff:bootRun --args='--server.address=127.0.0.1'
   ```

2. Start the web app at [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Vite forwards API requests to the BFF.

   ```sh
   ./gradlew :web:dev
   ```

3. Start the documentation at [http://127.0.0.1:8081/](http://127.0.0.1:8081/).

   ```sh
   ./gradlew :docs-site:serve -PdocsAppUrl=http://127.0.0.1:5173/
   ```

The configured docs home shows **Open demo**. Omit `-PdocsAppUrl` to show **Read quick start**.

## Select a demo role

Open the web app. **Demo role** starts on **Administrator** in a fresh tab. Select **Maya Chen** or **Alex Rivera** from the same directory. Reload the tab to verify that the selection persists, or open the app in a separate tab to start with Administrator.

If the directory request fails, check that the BFF is running, then choose **Retry loading roles** in the app.

## Extend the API contract

The implemented `listDemoRoles` operation, `GET /api/demo-roles`, starts in the [BFF OpenAPI document](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/bff/src/main/resources/static/openapi.json). Match its declared status, content type and response schema in the running Spring controller. The BFF component suite checks responses over HTTP against the served contract. The web checks exercise the generated Fetch client and its response validation.

```sh
./gradlew :bff:componentTest :web:generateClient :web:webCheck
```

Follow the same contract, server and generated-consumer sequence for each subsequent command, read or live operation.
