import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";
import tailwindcss from "@tailwindcss/vite";
import { playwright } from "@vitest/browser-playwright";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  cacheDir: "build/vitest-cache",
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  server: {
    fs: {
      // The disposable proof shares the installed dependencies with this project.
      allow: [
        fileURLToPath(new URL(".", import.meta.url)),
        realpathSync(new URL("./node_modules", import.meta.url)),
      ],
    },
  },
  plugins: [tailwindcss()],
  test: {
    projects: [
      {
        extends: true,
        plugins: [storybookTest({ configDir: fileURLToPath(new URL("./.storybook", import.meta.url)) })],
        test: {
          name: "storybook",
          browser: {
            enabled: true,
            headless: true,
            provider: playwright(),
            instances: [{ browser: "chromium" }],
          },
        },
      },
    ],
  },
});
