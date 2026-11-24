import { TypeID } from "typeid-js";

// The probe uses only these Node APIs, keeping its npm dependencies limited to the two candidates.
declare const process: {
  env: Record<string, string | undefined>;
  version: string;
  platform: string;
  arch: string;
  getBuiltinModule(id: "node:fs"): {
    readFileSync(file: string, encoding: "utf8"): string;
    writeFileSync(file: string, data: string, options: { flag: "wx" }): void;
  };
  getBuiltinModule(id: "node:assert/strict"): {
    equal(actual: unknown, expected: unknown, message: string): void;
    throws(action: () => unknown, expected: RegExp, message: string): void;
  };
  getBuiltinModule(id: "node:test"): { test(name: string, action: () => void): void };
};

const { readFileSync, writeFileSync } = process.getBuiltinModule("node:fs");
const { equal, throws } = process.getBuiltinModule("node:assert/strict");
const { test } = process.getBuiltinModule("node:test");

type JsonObject = Record<string, unknown>;
type Sample = { tag: string; prefix: string; uuid: Uint8Array };

const tags = new Map([["courseId", "course"], ["studentId", "student"]]);

function object(value: unknown, label: string): JsonObject {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`Expected an object for ${label}`);
  }
  return value as JsonObject;
}

function readObject(file: string): JsonObject {
  const parsed: unknown = JSON.parse(readFileSync(file, "utf8"));
  return object(parsed, file);
}

function field(value: JsonObject, name: string): string {
  const result = value[name];
  if (typeof result !== "string") throw new Error(`Expected string field ${name}`);
  return result;
}

function rows(root: JsonObject, name: string): JsonObject[] {
  const values = root[name];
  if (!Array.isArray(values)) throw new Error(`Expected array field ${name}`);
  return values.map((value: unknown) => object(value, name));
}

function requiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) throw new Error(`Missing environment value ${key}`);
  return value;
}

function uuidBytes(uuid: string): Uint8Array {
  if (!/^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(uuid)) {
    throw new Error(`Expected a canonical UUID: ${uuid}`);
  }
  const hex = uuid.replaceAll("-", "");
  return Uint8Array.from({ length: 16 }, (_, index) =>
    Number.parseInt(hex.slice(index * 2, index * 2 + 2), 16),
  );
}

function bytesHex(bytes: Uint8Array): string {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function validateId(value: string, prefix: string, uuid: Uint8Array, label: string): void {
  const decoded = TypeID.fromString(value, prefix);
  equal(decoded.getType(), prefix, `${label} decoded prefix`);
  equal(bytesHex(decoded.toUUIDBytes()), bytesHex(uuid), `${label} decoded UUID bytes`);
  equal(TypeID.fromUUIDBytes(prefix, uuid).toString(), value, `${label} canonical encoding`);
}

function samples(fixture: JsonObject, origin: string): Sample[] {
  const values = rows(fixture, origin);
  equal(values.length, tags.size, `${origin} sample count`);
  return Array.from(tags, ([tag, prefix]) => {
    const matches = values.filter((value) => field(value, "tag") === tag);
    equal(matches.length, 1, `${origin} ${tag} occurs exactly once`);
    equal(field(matches[0], "prefix"), prefix, `${origin} ${tag} prefix`);
    const uuid = uuidBytes(field(matches[0], "uuid"));
    equal(uuid[6] >>> 4, 7, `${origin} ${tag} UUID version`);
    equal(uuid[8] >>> 6, 2, `${origin} ${tag} UUID variant`);
    return { tag, prefix, uuid };
  });
}

function validateExchange(
  exchange: JsonObject,
  origin: string,
  expected: Sample[],
  runId: string,
  exchangeId: string,
): number {
  equal(field(exchange, "runId"), runId, `${origin} run ID`);
  equal(field(exchange, "exchangeId"), exchangeId, `${origin} exchange ID`);
  equal(field(exchange, "origin"), origin, `${origin} producer identity`);
  const vectors = rows(exchange, "vectors");
  equal(vectors.length, expected.length, `${origin} vector count`);
  for (const { tag, prefix, uuid } of expected) {
    const matches = vectors.filter((vector) => field(vector, "tag") === tag);
    equal(matches.length, 1, `${origin} ${tag} occurs exactly once`);
    const vector = matches[0];
    const label = `${origin} ${tag}`;
    equal(field(vector, "prefix"), prefix, `${label} prefix`);
    equal(field(vector, "uuidBytes"), bytesHex(uuid), `${label} UUID bytes`);
    validateId(field(vector, "typeid"), prefix, uuid, label);
  }
  return vectors.length;
}

test("Kotlin exchange belongs to the current TypeScript invocation", () => {
  const fixture = readObject(requiredEnv("PROBE_TYPEID_FIXTURE"));
  const source = object(fixture.source, "source");
  const positives = rows(fixture, "valid");
  const negatives = rows(fixture, "invalid");
  for (const vector of positives) {
    validateId(field(vector, "typeid"), field(vector, "prefix"), uuidBytes(field(vector, "uuid")), field(vector, "name"));
  }
  for (const vector of negatives) {
    throws(() => TypeID.fromString(field(vector, "typeid")), /./, `Rejected ${field(vector, "name")}`);
  }

  const inbound = readObject(requiredEnv("PROBE_TYPEID_KOTLIN"));
  const runId = requiredEnv("PROBE_TYPEID_RUN_ID");
  equal(field(inbound, "exchangeId"), process.env.PROBE_TYPEID_EXCHANGE_ID, "Kotlin exchange ID must match the current invocation");
  const exchangeId = requiredEnv("PROBE_TYPEID_EXCHANGE_ID");
  const kotlin = samples(fixture, "kotlin");
  const checked = validateExchange(inbound, "kotlin", kotlin, runId, exchangeId);
  const [first, ...rest] = rows(inbound, "vectors");
  const firstBytes = field(first, "uuidBytes");
  const changedByte = (Number.parseInt(firstBytes.slice(0, 2), 16) ^ 1).toString(16).padStart(2, "0");
  const changedVectors = (change: JsonObject) => ({ ...inbound, vectors: [{ ...first, ...change }, ...rest] });
  throws(
    () => validateExchange(changedVectors({ uuidBytes: changedByte + firstBytes.slice(2) }), "kotlin", kotlin, runId, exchangeId),
    /UUID bytes/,
    "TypeScript rejects a changed Kotlin UUID byte",
  );
  throws(
    () => validateExchange(changedVectors({ prefix: "different" }), "kotlin", kotlin, runId, exchangeId),
    /prefix/,
    "TypeScript rejects a changed Kotlin prefix",
  );
  throws(
    () => validateExchange({ ...inbound, exchangeId: "previous-invocation" }, "kotlin", kotlin, runId, exchangeId),
    /exchange ID/,
    "TypeScript rejects stale Kotlin output",
  );

  const inputs = samples(fixture, "typescript");
  const student = inputs[1];
  const studentId = TypeID.fromUUIDBytes(student.prefix, student.uuid).toString();
  throws(() => TypeID.fromString(studentId, "course"), /./, "A student TypeID cannot use the course slot");
  const exchange = {
    origin: "typescript",
    runId,
    exchangeId,
    vectors: inputs.map(({ tag, prefix, uuid }) => ({
      tag,
      prefix,
      uuidBytes: bytesHex(uuid),
      typeid: TypeID.fromUUIDBytes(prefix, uuid).toString(),
    })),
    sourceRevision: field(source, "revision"),
    positiveVectors: positives.length,
    negativeVectors: negatives.length,
    validatedKotlinVectors: checked,
    nodeVersion: process.version,
    npmVersion: /^npm\/([0-9.]+)\s/.exec(requiredEnv("npm_config_user_agent"))?.[1],
    typeidJsVersion: field(readObject("node_modules/typeid-js/package.json"), "version"),
    typescriptVersion: field(readObject("node_modules/typescript/package.json"), "version"),
    nativeCompiler: field(readObject(`node_modules/@typescript/typescript-${process.platform}-${process.arch}/package.json`), "name"),
    uuidVersion: field(readObject("node_modules/uuid/package.json"), "version"),
  };
  validateExchange(exchange, "typescript", inputs, runId, exchangeId);
  writeFileSync(requiredEnv("PROBE_TYPEID_TYPESCRIPT"), JSON.stringify(exchange, null, 2) + "\n", { flag: "wx" });
});
