import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

function resolveDocsBase(value: string): string {
  const url = URL.parse(value);
  if (
    !url ||
    !/^https?:\/\/[^/]/i.test(value) ||
    /[\s\\]/.test(value) ||
    url.href !== url.origin + url.pathname
  ) {
    throw new Error(
      "VITE_DOCS_BASE must be an absolute HTTP(S) documentation directory URL.",
    );
  }

  if (!url.pathname.endsWith("/")) url.pathname += "/";
  return url.href;
}

export default defineConfig(({ command, mode }) => {
  const envDir = fileURLToPath(new URL(".", import.meta.url));
  const env = loadEnv(mode, envDir, "VITE_");
  const docsBase = resolveDocsBase(
    env.VITE_DOCS_BASE ?? "http://127.0.0.1:8081/",
  );
  const config = {
    envDir,
    plugins: [react(), tailwindcss()],
    define: { "import.meta.env.VITE_DOCS_BASE": JSON.stringify(docsBase) },
    resolve: {
      alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
    },
    build: { outDir: "build/dist" },
  };
  if (command === "build") return config;

  const bff = new URL(env.VITE_BFF_ORIGIN ?? "http://127.0.0.1:8080");
  const isLoopback = ["127.0.0.1", "localhost", "[::1]"].includes(bff.hostname);
  if (
    !isLoopback ||
    !["http:", "https:"].includes(bff.protocol) ||
    bff.href !== bff.origin + "/"
  ) {
    throw new Error("VITE_BFF_ORIGIN must be an HTTP(S) loopback origin.");
  }

  return {
    ...config,
    server: {
      host: "127.0.0.1",
      strictPort: true,
      proxy: { "^/api(?:/|$)": bff.origin },
    },
  };
});
