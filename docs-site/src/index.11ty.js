import { escapeHtml } from "./_includes/page.11ty.js";

export const data = { layout: "page.11ty.js", title: "Run the demo" };

export function render({ launch }) {
  return `<h1>Run the demo</h1>
<p>Explore how Axon 5 uses Dynamic Consistency Boundaries to enforce course enrollment rules.</p>
<p><a class="launch-action" href="${escapeHtml(launch.href)}">${launch.label}</a></p>`;
}
