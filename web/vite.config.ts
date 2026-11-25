import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ command, mode }) => {
  if (command === "build") {
    return { plugins: [react()], build: { outDir: "build/dist" } };
  }

  const env = loadEnv(mode, process.cwd(), "VITE_");
  const bff = new URL(env.VITE_BFF_ORIGIN ?? "http://127.0.0.1:8080");
  const isLoopback = ["127.0.0.1", "localhost", "[::1]"].includes(bff.hostname);
  if (!isLoopback || !["http:", "https:"].includes(bff.protocol) || bff.href !== bff.origin + "/") {
    throw new Error("VITE_BFF_ORIGIN must be an HTTP(S) loopback origin.");
  }

  return {
    plugins: [react()],
    build: { outDir: "build/dist" },
    server: {
      host: "127.0.0.1",
      strictPort: true,
      proxy: { "^/api(?:/|$)": bff.origin },
    },
  };
});
