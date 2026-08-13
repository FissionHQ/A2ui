import { useA2UIStore } from "../store/a2uiStore";

export type StreamResult = {
  domain: string | null;
  surfaceId: string | null;
  error: string | null;
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
  history: Array<{ role: "user" | "assistant"; content: string }> = [],
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
    return { domain: null, surfaceId: null, error: `SSE failed: ${res.status}` };
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (value) buf += decoder.decode(value, { stream: true });
    if (done) buf += decoder.decode();
    const parts = buf.split(/\r?\n\r?\n/);
    buf = done ? "" : parts.pop() || "";
    for (const chunk of parts) consume(store, chunk);
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
  };
}
