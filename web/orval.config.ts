import { defineConfig } from "orval";

const contractPath = process.env.BFF_OPENAPI_FILE;
if (!contractPath) {
  throw new Error("Generate the client through :web:generateClient.");
}

export default defineConfig({
  bff: {
    input: contractPath,
    output: {
      target: "./build/generated/client.ts",
      schemas: { path: "./build/generated/schemas", type: "zod" },
      client: "fetch",
      clean: true,
      override: { fetch: { runtimeValidation: true } },
    },
  },
});
