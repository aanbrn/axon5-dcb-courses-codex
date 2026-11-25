import type { Preview } from "@storybook/react-vite";
import "../src/app/theme.css";

const preview: Preview = {
  parameters: {
    a11y: {
      test: "error",
      options: {
        runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
      },
    },
  },
};

export default preview;
