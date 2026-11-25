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
      const used = new Set(["main-content"]);
      let section = "";
      for (const [index, token] of tokens.entries()) {
        if (token.type === "heading_open") {
          section = tokens[index + 1].content;
          const slug = slugify(section) || "section";
          let id = slug;
          for (let number = 2; used.has(id); number++) id = `${slug}-${number}`;
          token.attrSet("id", id);
          used.add(id);
        }
        if (token.type === "table_open" || token.type === "fence")
          token.meta = { section };
      }
    });

    function scrollRegion(token, kind) {
      const section = token.meta.section;
      const label = markdown.utils.escapeHtml(
        section ? `${kind} — ${section}` : kind,
      );
      return `<div class="scroll-region" role="region" aria-label="${label}" tabindex="0">`;
    }

    const renderFence = markdown.renderer.rules.fence;
    markdown.renderer.rules.fence = (tokens, index, ...args) =>
      `${scrollRegion(tokens[index], "Code sample")}${renderFence(tokens, index, ...args)}</div>\n`;
    markdown.renderer.rules.table_open = (
      tokens,
      index,
      options,
      _env,
      renderer,
    ) =>
      scrollRegion(tokens[index], "Data table") +
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
