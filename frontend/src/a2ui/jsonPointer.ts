export class JsonPointerError extends Error {
  constructor(pointer: string) {
    super(`Invalid JSON Pointer: ${pointer}`);
    this.name = "JsonPointerError";
  }
}

function unescape(token: string) {
  return token.replace(/~1/g, "/").replace(/~0/g, "~");
}

export function parsePointer(pointer: string): string[] {
  if (pointer === "") return [];
  if (!pointer.startsWith("/")) throw new JsonPointerError(pointer);
  return pointer.split("/").slice(1).map(unescape);
}

export function getPointer(doc: unknown, pointer: string): unknown {
  if (pointer === "" || pointer === "/") return doc;
  const tokens = parsePointer(pointer);
  let cur: unknown = doc;
  for (const token of tokens) {
    if (token === "@index") return undefined;
    if (Array.isArray(cur)) {
      const idx = Number(token);
      if (!Number.isInteger(idx) || idx >= cur.length) return undefined;
      cur = cur[idx];
    } else if (cur && typeof cur === "object") {
      cur = (cur as Record<string, unknown>)[token];
    } else {
      return undefined;
    }
  }
  return cur;
}

export function setPointer(doc: unknown, pointer: string, value: unknown): unknown {
  if (pointer === "" || pointer === "/") return value ?? {};
  const tokens = parsePointer(pointer);
  const root = doc && typeof doc === "object" ? (doc as Record<string, unknown>) : {};
  let cur: any = root;
  for (let i = 0; i < tokens.length - 1; i++) {
    const token = tokens[i];
    const nextIsIndex = /^\d+$/.test(tokens[i + 1]);
    if (Array.isArray(cur)) {
      const idx = Number(token);
      if (!cur[idx]) cur[idx] = nextIsIndex ? [] : {};
      cur = cur[idx];
    } else {
      if (cur[token] == null) cur[token] = nextIsIndex ? [] : {};
      cur = cur[token];
    }
  }
  const last = tokens[tokens.length - 1];
  if (value === null) {
    if (Array.isArray(cur) && /^\d+$/.test(last)) cur.splice(Number(last), 1);
    else if (cur && typeof cur === "object") delete cur[last];
    return root;
  }
  if (Array.isArray(cur) && /^\d+$/.test(last)) cur[Number(last)] = value;
  else cur[last] = value;
  return root;
}
