import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HomePage } from "@/pages/home";
import "./theme.css";

const docsBase = new URL(
  import.meta.env.VITE_DOCS_BASE || "http://127.0.0.1:8081/",
  window.location.origin,
);
if (!docsBase.pathname.endsWith("/")) docsBase.pathname += "/";

const root = document.getElementById("root");
if (!root) throw new Error("The application mount point is missing.");
createRoot(root).render(
  <StrictMode>
    <HomePage docsBase={docsBase} />
  </StrictMode>,
);
