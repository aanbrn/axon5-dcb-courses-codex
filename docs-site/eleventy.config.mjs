import { HtmlBasePlugin } from "@11ty/eleventy";

const localAppOrigin = "http://127.0.0.1:5173";

function parseAppUrl(value) {
  try {
    if (!/^https?:\/\//.test(value) || /[\s\\\p{Cc}]/u.test(value)) throw new Error();
    const url = new URL(value);
    if (url.username || url.password) throw new Error();
    return url;
  } catch {
    throw new Error("Expected an absolute HTTP(S) app URL without credentials.");
  }
}

function launchAction() {
  const trustedOrigins = new Set([localAppOrigin]);
  for (const origin of (process.env.DOCS_TRUSTED_APP_ORIGINS ?? "").split(",").filter(Boolean)) {
    const url = parseAppUrl(origin.trim());
    if (url.protocol !== "https:" || url.href !== `${url.origin}/`) {
      throw new Error("docsTrustedAppOrigins must contain comma-separated HTTPS origins.");
    }
    trustedOrigins.add(url.origin);
  }

  const configuredUrl = process.env.DOCS_APP_URL ?? "";
  if (!configuredUrl) return { label: "Read quick start", href: "/quick-start/" };

  const url = parseAppUrl(configuredUrl);
  if (!trustedOrigins.has(url.origin)) throw new Error("docsAppUrl must use a trusted app origin.");
  return { label: "Open demo", href: url.href };
}

export default function (eleventyConfig) {
  const pathPrefix = process.env.DOCS_BASE ?? "/";
  if (!/^\/(?:[A-Za-z0-9_-]+\/)*$/.test(pathPrefix)) {
    throw new Error("docsBase must be a slash-delimited deployment path, such as /courses/.");
  }

  eleventyConfig.addPlugin(HtmlBasePlugin);
  eleventyConfig.addGlobalData("launch", launchAction());
  eleventyConfig.setServerOptions({ host: "127.0.0.1", showAllHosts: false, liveReload: false });

  const slugify = eleventyConfig.getFilter("slugify");
  eleventyConfig.amendLibrary("md", (markdown) => {
    markdown.core.ruler.push("heading_anchors", ({ tokens }) => {
      const used = new Set(["main-content"]);
      for (const [index, token] of tokens.entries()) {
        if (token.type !== "heading_open") continue;
        const slug = slugify(tokens[index + 1].content) || "section";
        let id = slug;
        for (let number = 2; used.has(id); number++) id = `${slug}-${number}`;
        token.attrSet("id", id);
        used.add(id);
      }
    });
  });

  return { pathPrefix, templateFormats: ["11ty.js", "md"], markdownTemplateEngine: false };
}
