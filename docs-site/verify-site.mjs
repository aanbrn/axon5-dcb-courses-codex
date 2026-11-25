import { readdirSync, readFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

export const publicFiles = new Set([
  "index.html",
  "quick-start/index.html",
  "feasibility/phase-01/index.html",
  "maintainer-guide/index.html",
  "site.css",
]);
const siteOrigin = "https://docs.invalid";
const entities = { amp: "&", apos: "'", gt: ">", lt: "<", quot: '"' };

function* elements(html) {
  for (const [, attributes] of html.matchAll(
    /<[a-z][\w:-]*\b((?:[^"'<>]|"[^"]*"|'[^']*')*)>/gi,
  )) {
    yield new Map(
      Array.from(
        attributes.matchAll(/\s([\w:-]+)=(?:"([^"]*)"|'([^']*)')/g),
        ([, name, double, single]) => [
          name.toLowerCase(),
          (double ?? single).replace(
            /&(#\d+|#x[\da-f]+|amp|apos|gt|lt|quot);/gi,
            (_, entity) => {
              if (!entity.startsWith("#"))
                return entities[entity.toLowerCase()];
              const codePoint = Number(
                entity.toLowerCase().replace(/^#x/, "0x").replace(/^#/, ""),
              );
              return codePoint > 0 && codePoint <= 0x10ffff
                ? String.fromCodePoint(codePoint)
                : "\uFFFD";
            },
          ),
        ],
      ),
    );
  }
}

export function verifyPublication(
  directory,
  base,
  { excludedName, excludedBytes } = {},
) {
  const files = new Map();
  for (const entry of readdirSync(directory, {
    recursive: true,
    withFileTypes: true,
  })) {
    const path = join(entry.parentPath, entry.name);
    const name = relative(directory, path).split(sep).join("/");
    if (excludedName && name.includes(excludedName))
      throw new Error(`Excluded fixture filename: ${name}`);
    if (
      entry.isDirectory() &&
      Array.from(publicFiles).some((file) => file.startsWith(`${name}/`))
    )
      continue;
    if (!entry.isFile() || !publicFiles.has(name))
      throw new Error(`Unexpected public artifact: ${name}`);
    const bytes = readFileSync(path);
    if (excludedBytes && bytes.includes(excludedBytes))
      throw new Error(`Excluded fixture bytes in ${name}`);
    if (bytes.length === 0) throw new Error(`Empty public artifact: ${name}`);
    files.set(name, bytes);
  }

  const pages = new Map();
  for (const name of publicFiles) {
    if (!files.has(name)) throw new Error(`Missing public artifact: ${name}`);
    if (name.endsWith(".html"))
      pages.set(name, Array.from(elements(files.get(name).toString("utf8"))));
  }

  for (const [name, tags] of pages) {
    const page = `${siteOrigin}${base}${name.replace(/index\.html$/, "")}`;
    for (const attributes of tags) {
      for (const link of [attributes.get("href"), attributes.get("src")]) {
        if (link === undefined || /^https?:\/\//i.test(link)) continue;
        const target = new URL(link, page);
        if (target.origin !== siteOrigin || !target.pathname.startsWith(base)) {
          throw new Error(`Invalid site link in ${name}: ${link}`);
        }
        let destination = decodeURIComponent(
          target.pathname.slice(base.length),
        );
        if (target.pathname.endsWith("/")) destination += "index.html";
        if (!files.has(destination))
          throw new Error(`Missing destination in ${name}: ${link}`);
        if (target.hash) {
          const id = decodeURIComponent(target.hash.slice(1));
          if (
            !pages.get(destination)?.some((element) => element.get("id") === id)
          ) {
            throw new Error(`Missing fragment in ${name}: ${link}`);
          }
        }
      }
    }
  }
}
