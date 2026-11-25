import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ command, mode }) => {
  const config = {
    plugins: [react(), tailwindcss()],
    resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
    build: { outDir: "build/dist" },
  };
  if (command === "build") return config;

  const env = loadEnv(mode, process.cwd(), "VITE_");
  const bff = new URL(env.VITE_BFF_ORIGIN ?? "http://127.0.0.1:8080");
  const isLoopback = ["127.0.0.1", "localhost", "[::1]"].includes(bff.hostname);
  if (!isLoopback || !["http:", "https:"].includes(bff.protocol) || bff.href !== bff.origin + "/") {
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
