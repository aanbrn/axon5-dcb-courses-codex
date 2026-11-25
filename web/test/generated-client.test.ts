import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import { after, test } from "node:test";
import { createServer as createViteServer } from "vite";

const vite = await createViteServer({
  configFile: false,
  appType: "custom",
  optimizeDeps: { noDiscovery: true },
  server: { middlewareMode: true, watch: null, ws: false },
});
after(() => vite.close());
const { loadDemoRoles } = (await vite.ssrLoadModule(
  "/src/shared/api/demoRoles.ts",
)) as typeof import("../src/shared/api/demoRoles.ts");

const administrator = {
  id: "admin",
  label: "Administrator",
  kind: "administrator",
};
const maya = { id: "maya", label: "Maya Chen", kind: "student" };
const alex = { id: "alex", label: "Alex Rivera", kind: "student" };
const directory = { administrator, students: [maya, alex] };

for (const students of [[], [maya], [alex, maya]]) {
  test(`returns the administrator and ${students.length} ordered students`, async (t) => {
    const payload = { administrator, students };
    const fetch = t.mock.method(globalThis, "fetch", async () =>
      Response.json(payload, {
        headers: { "Content-Type": "application/json; charset=utf-8" },
      }),
    );
    const signal = new AbortController().signal;

    assert.deepEqual(await loadDemoRoles(signal), payload);
    assert.equal(fetch.mock.callCount(), 1);
    const [url, options] = fetch.mock.calls[0].arguments;
    assert.equal(url, "/api/demo-roles");
    assert.equal(options?.method, "GET");
    assert.equal(options?.signal, signal);
  });
}

const invalidPayloads = {
  "missing administrator": { students: [] },
  "missing students": { administrator },
  "non-array students": { administrator, students: maya },
  "empty administrator ID": {
    ...directory,
    administrator: { ...administrator, id: "" },
  },
  "wrong administrator discriminator": {
    ...directory,
    administrator: { ...administrator, kind: "student" },
  },
  "missing student label": {
    administrator,
    students: [{ id: "maya", kind: "student" }],
  },
  "empty student label": { administrator, students: [{ ...maya, label: "" }] },
  "wrong student discriminator": {
    administrator,
    students: [{ ...maya, kind: "administrator" }],
  },
};

for (const [name, payload] of Object.entries(invalidPayloads)) {
  test(`the generated schema rejects ${name}`, async (t) => {
    t.mock.method(globalThis, "fetch", async () => Response.json(payload));

    await assert.rejects(loadDemoRoles(), { name: "ZodError" });
  });
}

for (const [name, students] of [
  [
    "a shared administrator and student ID",
    [{ ...maya, id: administrator.id }],
  ],
  ["a repeated student ID", [maya, { ...alex, id: maya.id }]],
] as const) {
  test(`rejects ${name}`, async (t) => {
    t.mock.method(globalThis, "fetch", async () =>
      Response.json({ administrator, students }),
    );

    await assert.rejects(loadDemoRoles(), /duplicate identifiers/);
  });
}

test("rejects invalid JSON with the documented status and media type", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () =>
      new Response('{"administrator":', {
        headers: { "content-type": "application/json" },
      }),
  );

  await assert.rejects(loadDemoRoles(), SyntaxError);
});

for (const mediaType of [
  "text/json",
  "application/problem+json",
  "text/plain",
]) {
  test(`rejects the undocumented ${mediaType} media type`, async (t) => {
    t.mock.method(globalThis, "fetch", async () =>
      Response.json(directory, { headers: { "content-type": mediaType } }),
    );

    await assert.rejects(loadDemoRoles(), /must be JSON/);
  });
}

test("rejects a successful status other than HTTP 200", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    Response.json(directory, { status: 201 }),
  );

  await assert.rejects(loadDemoRoles(), /HTTP 201/);
});

test(
  "rejects a redirect to a valid role directory",
  { timeout: 5_000 },
  async (t) => {
    const fetch = globalThis.fetch;
    let replacementRequests = 0;
    const server = createServer((request, response) => {
      if (request.url === "/api/demo-roles") {
        response.writeHead(302, { location: "/replacement" }).end();
        return;
      }
      replacementRequests++;
      response
        .writeHead(200, { "content-type": "application/json" })
        .end(JSON.stringify(directory));
    });
    const listening = once(server, "listening");
    server.listen(0, "127.0.0.1");
    await listening;
    t.after(async () => {
      server.close();
      await once(server, "close");
    });
    const address = server.address();
    assert(address && typeof address === "object");
    const origin = `http://127.0.0.1:${address.port}`;
    t.mock.method(globalThis, "fetch", (url: string, options: RequestInit) =>
      fetch(new URL(url, origin), options),
    );

    await assert.rejects(loadDemoRoles(), TypeError);
    assert.equal(replacementRequests, 0);
  },
);
