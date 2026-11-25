import fsd from "@feature-sliced/steiger-plugin";
import { defineConfig } from "steiger";

export default defineConfig([
  { ignores: ["**/build/**", "**/node_modules/**"] },
  ...fsd.configs.recommended,
]);
