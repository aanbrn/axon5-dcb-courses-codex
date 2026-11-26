import { join } from "node:path";
import { HtmlBasePlugin } from "@11ty/eleventy";
import { verifyPublication } from "./verify-site.mjs";

const localAppOrigin = "http://127.0.0.1:5173";

function parseAppUrl(value) {
  try {
    if (!/^https?:\/\/[^/?#]+/.test(value) || /[\s\\\p{Cc}]/u.test(value))
      throw new Error();
    const url = new URL(value);
    if (url.username || url.password) throw new Error();
    return url;
  } catch {
    throw new Error(
      "Expected an absolute HTTP(S) app URL without credentials.",
    );
  }
}

function launchAction() {
  const trustedOrigins = new Set([localAppOrigin]);
  for (const origin of (process.env.DOCS_TRUSTED_APP_ORIGINS ?? "")
    .split(",")
    .filter(Boolean)) {
    const url = parseAppUrl(origin.trim());
    if (url.protocol !== "https:" || url.href !== `${url.origin}/`) {
      throw new Error(
        "docsTrustedAppOrigins must contain comma-separated HTTPS origins.",
      );
    }
    trustedOrigins.add(url.origin);
  }

  const configuredUrl = process.env.DOCS_APP_URL ?? "";
  if (!configuredUrl)
    return { label: "Read quick start", href: "/quick-start/" };

  const url = parseAppUrl(configuredUrl);
  if (!trustedOrigins.has(url.origin))
    throw new Error("docsAppUrl must use a trusted app origin.");
  return { label: "Open demo", href: url.href };
}

function inlineText({ children }) {
  return children
    .map((token) => {
      if (token.type === "text" || token.type === "code_inline")
        return token.content;
      if (token.type === "image") return inlineText(token);
      if (token.type === "softbreak" || token.type === "hardbreak") return " ";
      return "";
    })
    .join("")
    .replace(/\s+/g, " ")
    .trim();
}

function regionDescription(tokens, index) {
  if (tokens[index - 1]?.type !== "paragraph_close") return "";
  const text = inlineText(tokens[index - 2]);
  if (text.length <= 80 && text.endsWith(":")) return text.slice(0, -1).trim();

  if (
    tokens[index].type !== "fence" ||
    tokens[index - 4]?.type !== "list_item_open"
  )
    return "";
  const [firstSentence] = text.split(/[.!?](?=\s|$)/, 1);
  const step = firstSentence.replace(/ at https?:\/\/\S+$/i, "").trim();
  return step.length <= 80 ? step : "";
}

export default function (eleventyConfig) {
  const input = process.env.DOCS_INPUT ?? "build/staged";
  const pathPrefix = process.env.DOCS_BASE ?? "/";
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(pathPrefix)) {
    throw new Error(
      "docsBase must be a slash-delimited deployment path, such as /courses/.",
    );
  }

  eleventyConfig.addPlugin(HtmlBasePlugin);
  eleventyConfig.addGlobalData("launch", launchAction());
  eleventyConfig.addPassthroughCopy({
    [join(input, "site.css")]: "site.css",
    [join(input, "fonts")]: "fonts",
  });
  eleventyConfig.on("eleventy.after", ({ directories, outputMode }) => {
    if (outputMode === "fs") verifyPublication(directories.output, pathPrefix);
  });

  const slugify = eleventyConfig.getFilter("slugify");
  eleventyConfig.amendLibrary("md", (markdown) => {
    markdown.core.ruler.push("article_accessibility", ({ tokens }) => {
      const usedHeadingIds = new Set(["main-content"]);
      const regions = [];
      let section = { title: "Article", id: "main-content", counts: new Map() };
      for (const [index, token] of tokens.entries()) {
        if (token.type === "heading_open") {
          const heading = tokens[index + 1];
          const slug = slugify(heading.content) || "section";
          let id = slug;
          for (let number = 2; usedHeadingIds.has(id); number++)
            id = `${slug}-${number}`;
          token.attrSet("id", id);
          usedHeadingIds.add(id);
          section = { title: inlineText(heading) || id, id, counts: new Map() };
        }
        if (token.type !== "table_open" && token.type !== "fence") continue;
        const kind = token.type === "table_open" ? "Data table" : "Code sample";
        const ordinal = (section.counts.get(kind) ?? 0) + 1;
        section.counts.set(kind, ordinal);
        regions.push({
          token,
          kind,
          section,
          ordinal,
          description: regionDescription(tokens, index),
        });
      }

      const usedLabels = new Set();
      for (const { token, kind, section, ordinal, description } of regions) {
        let label = `${kind} — ${section.title}`;
        if (description) label += ` — ${description}`;
        else if (section.counts.get(kind) > 1) label += ` (${ordinal})`;
        if (usedLabels.has(label)) label += ` (${section.id})`;

        let unique = label;
        for (let number = ordinal; usedLabels.has(unique); number++)
          unique = `${label} (${number})`;
        usedLabels.add(unique);
        (token.meta ??= {}).scrollRegionName = unique;
      }
    });

    function scrollRegion(token) {
      const label = markdown.utils.escapeHtml(token.meta.scrollRegionName);
      return `<div class="scroll-region" role="region" aria-label="${label}" tabindex="0">`;
    }

    const renderFence = markdown.renderer.rules.fence;
    markdown.renderer.rules.fence = (tokens, index, ...args) =>
      `${scrollRegion(tokens[index])}${renderFence(tokens, index, ...args)}</div>\n`;
    markdown.renderer.rules.table_open = (
      tokens,
      index,
      options,
      _env,
      renderer,
    ) =>
      scrollRegion(tokens[index]) +
      renderer.renderToken(tokens, index, options);
    markdown.renderer.rules.table_close = (
      tokens,
      index,
      options,
      _env,
      renderer,
    ) => renderer.renderToken(tokens, index, options) + "</div>\n";
  });

  return {
    dir: { input },
    pathPrefix,
    templateFormats: ["11ty.js", "md"],
    markdownTemplateEngine: false,
  };
}
