import { readdirSync, readFileSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { html, parse } from "parse5";

export const publicFiles = new Set([
  "index.html",
  "quick-start/index.html",
  "feasibility/phase-01/index.html",
  "maintainer-guide/index.html",
  "site.css",
  "fonts/geist-latin-wght-normal.woff2",
  "fonts/geist-mono-latin-wght-normal.woff2",
  "fonts/geist-LICENSE.txt",
  "fonts/geist-mono-LICENSE.txt",
]);
const siteOrigin = "https://docs.invalid";

function indexPage(markup, source) {
  const links = [];
  const fragments = new Set();
  const pending = [parse(markup)];
  while (pending.length > 0) {
    const { attrs, childNodes = [], tagName, namespaceURI } = pending.pop();
    if (attrs) {
      const attribute = (name) =>
        attrs.find((item) => item.name === name && !item.namespace)?.value;
      const href = attribute("href");
      const src = attribute("src");
      const id = attribute("id");
      const isHtml = namespaceURI === html.NS.HTML;
      if (isHtml && tagName === "base" && href !== undefined)
        throw new Error(
          `Active base href in ${source}: ${JSON.stringify(href)}`,
        );
      if (href !== undefined) links.push(href);
      if (src !== undefined) links.push(src);
      if (id !== undefined) fragments.add(id);
      if (isHtml && tagName === "a") {
        const name = attribute("name");
        if (name !== undefined) fragments.add(name);
      }
    }
    // The template's inert document fragment is separate from childNodes.
    for (let index = childNodes.length - 1; index >= 0; index--)
      pending.push(childNodes[index]);
  }
  return { links, fragments };
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
      pages.set(name, indexPage(files.get(name).toString("utf8"), name));
  }

  for (const [name, { links }] of pages) {
    const page = `${siteOrigin}${base}${name.replace(/index\.html$/, "")}`;
    for (const link of links) {
      if (/^https?:\/\//i.test(link)) continue;
      const target = new URL(link, page);
      if (target.origin !== siteOrigin || !target.pathname.startsWith(base)) {
        throw new Error(`Invalid site link in ${name}: ${link}`);
      }
      // The preview looks up the request pathname verbatim.
      let destination = target.pathname.slice(base.length);
      if (target.pathname.endsWith("/")) destination += "index.html";
      if (!files.has(destination))
        throw new Error(`Missing destination in ${name}: ${link}`);
      if (target.hash) {
        const id = decodeURIComponent(target.hash.slice(1));
        if (!pages.get(destination)?.fragments.has(id))
          throw new Error(`Missing fragment in ${name}: ${link}`);
      }
    }
  }
}
