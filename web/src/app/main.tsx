import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HomePage } from "@/pages/home";
import "./theme.css";

const docsBase = new URL(import.meta.env.VITE_DOCS_BASE);

const root = document.getElementById("root");
if (!root) throw new Error("The application mount point is missing.");
createRoot(root).render(
  <StrictMode>
    <HomePage docsBase={docsBase} />
  </StrictMode>,
);
