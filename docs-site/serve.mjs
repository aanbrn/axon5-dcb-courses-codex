import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join } from "node:path";
import { publicFiles } from "./verify-site.mjs";

const [, , directory, base] = process.argv;
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".woff2": "font/woff2",
};
const routes = new Map();
for (const file of publicFiles) {
  const type = contentTypes[extname(file)];
  const bytes = readFileSync(join(directory, file));
  const asset = { type, bytes };
  routes.set(base + file, asset);
  if (file.endsWith("index.html"))
    routes.set(base + file.slice(0, -"index.html".length), asset);
}

const server = createServer((request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end();
    return;
  }
  const path = request.url.split("?", 1)[0];
  if (base !== "/" && path === base.slice(0, -1)) {
    response.writeHead(308, { Location: base }).end();
    return;
  }
  const asset = routes.get(path);
  if (!asset) {
    response.writeHead(404).end();
    return;
  }
  response.writeHead(200, {
    "Content-Type": asset.type,
    "Content-Length": asset.bytes.length,
  });
  response.end(request.method === "HEAD" ? undefined : asset.bytes);
});

server.listen(8081, "127.0.0.1", () => {
  const { address, port } = server.address();
  console.log(`Serving documentation at http://${address}:${port}${base}`);
});
