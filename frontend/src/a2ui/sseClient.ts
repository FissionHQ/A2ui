import { useA2UIStore } from "../store/a2uiStore";

export type StreamResult = {
  domain: string | null;
  surfaceId: string | null;
  error: string | null;
  routing: RoutingState | null;
};

export type RoutingState = {
  domain: string;
  intent?: string;
  entities: Record<string, unknown>;
  focus?: string;
  confidence?: number;
  missingFields?: string[];
  clarificationQuestion?: string;
};

function consume(store: ReturnType<typeof useA2UIStore.getState>, chunk: string) {
  const dataLine = chunk
    .replace(/\r/g, "")
    .split("\n")
    .filter((l) => l.startsWith("data:"))
    .map((l) => l.slice(5).trimStart())
    .join("");
  if (!dataLine || dataLine === "{}") return;
  try {
    store.applyMessage(JSON.parse(dataLine));
  } catch {
    store.applyMessage({
      version: "demo",
      agentActivity: { step: "parse", detail: "Malformed SSE payload", status: "error" },
    });
  }
}

function domainFromActivity(store: ReturnType<typeof useA2UIStore.getState>): string | null {
  const hit = store.activity.find((a) => a.detail.toLowerCase().includes("intent detected"));
  if (!hit) return null;
  return hit.detail.replace(/^Intent detected:\s*/i, "").trim() || null;
}

export async function streamIntent(
  text: string,
  userContext: unknown,
  history: Array<{ role: "user" | "assistant"; content: string; state?: RoutingState }> = [],
): Promise<StreamResult> {
  const store = useA2UIStore.getState();
  store.beginTurn();
  const res = await fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ text, userContext, history }),
  });
  if (!res.ok || !res.body) {
    store.applyMessage({
      version: "demo",
      agentActivity: { step: "sse", detail: `SSE failed: ${res.status}`, status: "error" },
    });
    return { domain: null, surfaceId: null, error: `SSE failed: ${res.status}`, routing: null };
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let routing: RoutingState | null = null;
  while (true) {
    const { done, value } = await reader.read();
    if (value) buf += decoder.decode(value, { stream: true });
    if (done) buf += decoder.decode();
    const parts = buf.split(/\r?\n\r?\n/);
    buf = done ? "" : parts.pop() || "";
    for (const chunk of parts) {
      const line = chunk.replace(/\r/g, "").split("\n").find((l) => l.startsWith("data:"));
      if (line) {
        try {
          const parsed = JSON.parse(line.slice(5).trimStart()) as { routingResult?: RoutingState };
          if (parsed.routingResult) routing = parsed.routingResult;
        } catch { /* regular consumer reports malformed payloads */ }
      }
      consume(store, chunk);
    }
    if (done) {
      if (buf.trim()) consume(store, buf);
      break;
    }
  }
  const final = useA2UIStore.getState();
  return {
    domain: domainFromActivity(final),
    surfaceId: final.activeSurfaceId,
    error: final.canvasError,
    routing,
  };
}
