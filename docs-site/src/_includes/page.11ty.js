const navigation = [
  ["/", "Home"],
  ["/feasibility/phase-01/", "Feasibility report"],
];

export function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export default function ({ title, page, content }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)} | Axon 5 DCB Courses</title>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header>
    <nav aria-label="Documentation">
      ${navigation.map(([href, label]) => `<a href="${href}"${page.url === href ? ' aria-current="page"' : ""}>${label}</a>`).join("\n      ")}
    </nav>
  </header>
  <main id="main-content" tabindex="-1">
    ${content}
  </main>
</body>
</html>`;
}
