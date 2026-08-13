import { create } from "zustand";
import type { A2UIComponent, A2UIMessage, SurfaceState } from "../a2ui/types";
import { setPointer } from "../a2ui/jsonPointer";
import { CatalogError, validateMessage } from "../a2ui/validate";

type InspectorEntry = {
  id: string;
  ts: string;
  type: string;
  surfaceId?: string;
  payload: unknown;
};

type Activity = { detail: string; status?: string; ts: string };

type Store = {
  surfaces: Record<string, SurfaceState>;
  activeSurfaceId: string | None;
  previousSurfaceId: string | null;
  inspector: InspectorEntry[];
  activity: Activity[];
  pipelineStage: string;
  canvasError: string | null;
  applyMessage: (msg: A2UIMessage | Record<string, unknown>) => void;
  beginTurn: () => void;
  reset: () => void;
  restoreSurface: (surfaceId: string, surface: SurfaceState) => void;
  patchData: (surfaceId: string, path: string, value: unknown) => void;
};

type None = string | null;

function surfaceIdOf(msg: Record<string, unknown>): string | undefined {
  for (const k of ["createSurface", "updateComponents", "updateDataModel", "deleteSurface"]) {
    const body = msg[k] as { surfaceId?: string } | undefined;
    if (body?.surfaceId) return body.surfaceId;
  }
  return undefined;
}

function typeOf(msg: Record<string, unknown>): string {
  if (msg.version === "demo") {
    if ("agentActivity" in msg) return "agentActivity";
    if ("pipeline" in msg) return "pipeline";
    return "demo";
  }
  return (
    ["createSurface", "updateComponents", "updateDataModel", "deleteSurface", "actionResponse"].find((k) => k in msg) ||
    "unknown"
  );
}

export const useA2UIStore = create<Store>((set, get) => ({
  surfaces: {},
  activeSurfaceId: null,
  previousSurfaceId: null,
  inspector: [],
  activity: [],
  pipelineStage: "",
  canvasError: null,
  reset: () =>
    set({
      surfaces: {},
      activeSurfaceId: null,
      previousSurfaceId: null,
      inspector: [],
      activity: [],
      pipelineStage: "",
      canvasError: null,
    }),
  beginTurn: () =>
    set({
      inspector: [],
      activity: [],
      pipelineStage: "",
      canvasError: null,
    }),
  restoreSurface: (surfaceId, surface) =>
    set({
      surfaces: { [surfaceId]: structuredClone(surface) },
      activeSurfaceId: surfaceId,
      previousSurfaceId: null,
      canvasError: null,
    }),
  patchData: (surfaceId, path, value) => {
    const s = get().surfaces[surfaceId];
    if (!s) return;
    const cloned = structuredClone(s.dataModel);
    const next = setPointer(cloned, path, value) as Record<string, unknown>;
    set({
      surfaces: { ...get().surfaces, [surfaceId]: { ...s, dataModel: next } },
    });
  },
  applyMessage: (raw) => {
    const msg = raw as Record<string, unknown>;
    const entry: InspectorEntry = {
      id: crypto.randomUUID(),
      ts: new Date().toISOString(),
      type: typeOf(msg),
      surfaceId: surfaceIdOf(msg),
      payload: msg,
    };
    const inspector = [entry, ...get().inspector].slice(0, 80);

    try {
      validateMessage(msg as A2UIMessage);
    } catch (err) {
      set({ inspector, canvasError: err instanceof Error ? err.message : String(err) });
      return;
    }

    if (msg.version === "demo") {
      const act = msg.agentActivity as { detail: string; status?: string } | undefined;
      const pipe = msg.pipeline as { stage: string } | undefined;
      set({
        inspector,
        activity: act ? [{ ...act, ts: entry.ts }, ...get().activity].slice(0, 40) : get().activity,
        pipelineStage: pipe?.stage ?? get().pipelineStage,
      });
      return;
    }

    if ("createSurface" in msg) {
      const body = msg.createSurface as {
        surfaceId: string;
        catalogId?: string;
        components?: A2UIComponent[];
        dataModel?: Record<string, unknown>;
      };
      const prev = get().activeSurfaceId;
      const surfaces = { ...get().surfaces };
      if (prev && prev !== body.surfaceId && surfaces[prev]) {
        delete surfaces[prev];
      }
      const components: Record<string, A2UIComponent> = {};
      for (const c of body.components || []) components[c.id] = c;
      surfaces[body.surfaceId] = {
        catalog: body.catalogId || "AppCatalog",
        components,
        dataModel: body.dataModel || {},
        status: "creating",
      };
      set({
        surfaces,
        activeSurfaceId: body.surfaceId,
        previousSurfaceId: prev,
        inspector,
        canvasError: null,
      });
      return;
    }

    if ("updateComponents" in msg) {
      const body = msg.updateComponents as { surfaceId: string; components: A2UIComponent[] };
      const s = get().surfaces[body.surfaceId];
      if (!s) {
        set({ inspector, canvasError: `Unknown surface ${body.surfaceId}` });
        return;
      }
      const components = { ...s.components };
      for (const c of body.components) components[c.id] = c;
      set({
        inspector,
        canvasError: null,
        surfaces: {
          ...get().surfaces,
          [body.surfaceId]: { ...s, components, status: "ready" },
        },
        activeSurfaceId: body.surfaceId,
      });
      return;
    }

    if ("updateDataModel" in msg) {
      const body = msg.updateDataModel as { surfaceId: string; path?: string; value: unknown };
      const s = get().surfaces[body.surfaceId];
      if (!s) return;
      const next = setPointer(s.dataModel, body.path || "/", body.value) as Record<string, unknown>;
      set({
        inspector,
        surfaces: { ...get().surfaces, [body.surfaceId]: { ...s, dataModel: next, status: "ready" } },
      });
      return;
    }

    if ("deleteSurface" in msg) {
      const { surfaceId } = msg.deleteSurface as { surfaceId: string };
      const surfaces = { ...get().surfaces };
      delete surfaces[surfaceId];
      set({
        inspector,
        surfaces,
        activeSurfaceId: get().activeSurfaceId === surfaceId ? null : get().activeSurfaceId,
      });
      return;
    }

    if ("actionResponse" in msg) {
      set({ inspector });
    }
  },
}));

export { CatalogError };
