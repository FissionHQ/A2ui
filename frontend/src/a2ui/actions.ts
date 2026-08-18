import type { A2UIComponent } from "./types";
import { getPointer } from "./jsonPointer";
import { useA2UIStore } from "../store/a2uiStore";

function resolveContext(ctx: Record<string, unknown> | undefined, data: unknown, index?: number) {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(ctx || {})) {
    if (v && typeof v === "object" && "path" in (v as object)) {
      let path = String((v as { path: string }).path);
      if (typeof index === "number") path = path.replace("/@index/", `/${index}/`);
      out[k] = getPointer(data, path);
    } else out[k] = v;
  }
  return out;
}

export async function dispatchAction(
  comp: A2UIComponent,
  surfaceId: string,
  data: unknown,
  index?: number,
) {
  const action = comp.action;
  if (!action) return;
  if (action.functionCall) {
    const call = action.functionCall.call;
    const store = useA2UIStore.getState();
    if (call === "changeTab") {
      const path = String((action.functionCall.args as { path?: string } | undefined)?.path || "/news/activeTab");
      store.patchData(surfaceId, path, "ai");
      return;
    }
    if (call === "toggleCompare") {
      const product = typeof index === "number" ? getPointer(data, `/shopping/products/${index}`) : null;
      const current = getPointer(data, "/shopping/compared");
      const compared = Array.isArray(current) ? [...current] : [];
      const title = product && typeof product === "object" ? String((product as { title?: string }).title || "") : "";
      const exists = compared.findIndex((p) => p && typeof p === "object" && (p as { title?: string }).title === title);
      const next =
        exists >= 0
          ? compared.filter((_, i) => i !== exists)
          : title
            ? [...compared, product].slice(0, 3)
            : compared;
      store.patchData(surfaceId, "/shopping/compared", next);
      return;
    }
    if (call === "clearCompare") {
      store.patchData(surfaceId, "/shopping/compared", []);
      return;
    }
    store.canvasError = `Unsupported local functionCall: ${call}`;
    useA2UIStore.setState({ canvasError: `Unsupported local functionCall: ${call}` });
    return;
  }
  if (action.event) {
    const res = await fetch("/api/handle-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: action.event.name,
        surfaceId,
        actionId: crypto.randomUUID(),
        context: resolveContext(action.event.context, data, index),
      }),
    });
    const json = await res.json();
    const apply = useA2UIStore.getState().applyMessage;
    if (json.actionResponse) {
      apply({ version: "v1.0", actionResponse: json.actionResponse });
    }
    for (const m of json.messages || []) apply(m);
    if (json.actionResponse?.value) {
      window.dispatchEvent(new CustomEvent("a2ui-action-result", { detail: json.actionResponse.value }));
    }
  }
}
