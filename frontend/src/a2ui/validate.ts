import { CATALOG_ID, COMPONENT_NAMES, LOCAL_FUNCTIONS, type A2UIMessage } from "./types";

export class CatalogError extends Error {
  constructor(name: string) {
    super(`Unsupported A2UI component:\n${name}`);
    this.name = "CatalogError";
  }
}

export function validateMessage(msg: A2UIMessage | Record<string, unknown>) {
  if ((msg as { version?: string }).version === "demo") return;
  const rec = msg as Record<string, unknown>;
  const keys = ["createSurface", "updateComponents", "updateDataModel", "deleteSurface", "actionResponse"].filter(
    (k) => k in rec,
  );
  if (keys.length !== 1) throw new Error("Malformed message: expected exactly one A2UI key");
  const key = keys[0];
  const body = rec[key] as Record<string, unknown>;
  if (key === "createSurface" && body.catalogId && body.catalogId !== CATALOG_ID) {
    throw new Error(`Unsupported catalog: ${body.catalogId}`);
  }
  if (key === "updateComponents") {
    const comps = (body.components as Array<Record<string, unknown>>) || [];
    for (const c of comps) {
      const name = String(c.component ?? "");
      if (!COMPONENT_NAMES.includes(name as (typeof COMPONENT_NAMES)[number])) {
        throw new CatalogError(name);
      }
      if (Array.isArray(c.children) && c.children.some((ch) => typeof ch === "object")) {
        throw new Error("children must reference component IDs, not nested objects");
      }
      const action = c.action as { functionCall?: { call: string } } | undefined;
      if (action?.functionCall && !LOCAL_FUNCTIONS.has(action.functionCall.call)) {
        throw new Error(`Unsupported local functionCall: ${action.functionCall.call}`);
      }
    }
  }
  if (key === "updateDataModel") {
    const path = (body.path as string) ?? "/";
    if (path !== "/" && !path.startsWith("/")) throw new Error(`Invalid JSON Pointer: ${path}`);
  }
}
