import { useEffect, useMemo, useRef, useState } from "react";
import { Send, Smartphone, Monitor, Boxes, Trash2 } from "lucide-react";
import A2UIRenderer from "../a2ui/A2UIRenderer";
import { streamIntent } from "../a2ui/sseClient";
import { useA2UIStore } from "../store/a2uiStore";
import { useChatStore } from "../store/chatStore";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "What's the weather in Hyderabad tomorrow?",
  "Show me today's AI news.",
  "Plan a weekend trip to Goa.",
  "How is the Indian stock market doing?",
  "Find headphones under ₹10,000.",
  "Show me invoices that need attention.",
  "I want to release my freelancer milestone.",
  "My order is delayed. Can I get a refund?",
];

const USERS = [
  { id: "user-a", label: "SME Owner", role: "business-owner" },
  { id: "user-b", label: "Freelancer", role: "freelancer" },
  { id: "user-c", label: "Finance Manager", role: "finance-manager" },
];

const PIPELINE = [
  "USER",
  "INTENT_ROUTER",
  "DOMAIN_AGENTS",
  "A2UI_GENERATOR",
  "SSE",
  "A2UI_RUNTIME",
  "COMPONENT_CATALOG",
  "REACT",
];

type Health = {
  demoMode: boolean;
  llmProvider: string;
  llmModel: string;
  generationModel: string;
  dataMode: string;
  enabledDomains: string[];
};

export default function DemoShell() {
  const [text, setText] = useState("");
  const [device, setDevice] = useState<"desktop" | "mobile">("desktop");
  const [userIdx, setUserIdx] = useState(0);
  const [showArch, setShowArch] = useState(false);
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<Health | null>(null);
  const [openMsg, setOpenMsg] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const messages = useChatStore((s) => s.messages);
  const activeTurnId = useChatStore((s) => s.activeTurnId);
  const addUser = useChatStore((s) => s.addUser);
  const addAssistant = useChatStore((s) => s.addAssistant);
  const clearHistory = useChatStore((s) => s.clearHistory);
  const historyForApi = useChatStore((s) => s.historyForApi);
  const restoreSurface = useA2UIStore((s) => s.restoreSurface);
  const activeSurfaceId = useA2UIStore((s) => s.activeSurfaceId);
  const activity = useA2UIStore((s) => s.activity);
  const inspector = useA2UIStore((s) => s.inspector);
  const stage = useA2UIStore((s) => s.pipelineStage);
  const domainHint = useMemo(() => {
    const hit = activity.find((a) => a.detail.toLowerCase().includes("intent detected"));
    return hit?.detail.replace("Intent detected: ", "") ?? "—";
  }, [activity]);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, busy]);

  const user = USERS[userIdx];
  const context = {
    user: { id: user.id, role: user.role },
    device: { type: device },
    preferences: { compact: device === "mobile" },
    locale: "en-IN",
    currentIntent: text,
  };

  function replayTurn(id: string) {
    const msg = messages.find((m) => m.id === id);
    if (msg?.role === "assistant" && msg.surface && msg.surfaceId) {
      restoreSurface(msg.surfaceId, msg.surface);
      useChatStore.getState().setActiveTurn(id);
    }
  }

  async function submit(next = text) {
    const prompt = next.trim();
    if (!prompt) return;
    addUser(prompt);
    setText("");
    setBusy(true);
    try {
      const prior = historyForApi().slice(0, -1);
      const result = await streamIntent(prompt, { ...context, currentIntent: prompt }, prior);
      const surface = result.surfaceId ? useA2UIStore.getState().surfaces[result.surfaceId] : undefined;
      const label = result.error
        ? `Could not render: ${result.error}`
        : result.domain
          ? `${result.domain.replace(/_/g, " ")} experience ready`
          : "Experience updated";
      addAssistant({
        text: label,
        domain: result.domain ?? undefined,
        surfaceId: result.surfaceId ?? undefined,
        surface,
      });
    } finally {
      setBusy(false);
    }
  }

  function handleClearHistory() {
    clearHistory();
    useA2UIStore.getState().reset();
  }

  const openInspector = inspector.find((m) => m.id === openMsg);

  return (
    <div className="flex h-full min-h-screen bg-background text-foreground">
      <aside className="flex w-[400px] shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
        <header className="border-b border-sidebar-border px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
              A2
            </div>
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
                A2UI Adaptive Experience
              </div>
              <h1 className="text-base font-semibold leading-tight">One catalog. Many experiences.</h1>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {health?.demoMode !== false ? (
              <Badge variant="warning">DEMO MODE</Badge>
            ) : (
              <Badge variant="success">Live LLM: Gemini/{health?.llmModel}</Badge>
            )}
            <span className="text-xs text-sidebar-muted">{health?.dataMode ?? "mix"} APIs</span>
          </div>
        </header>

        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex items-center justify-between border-b border-sidebar-border px-5 py-2">
            <Label className="text-xs font-semibold uppercase tracking-wide text-sidebar-muted">Chat</Label>
            {messages.length > 0 ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 text-xs text-sidebar-muted hover:text-sidebar-foreground"
                onClick={handleClearHistory}
              >
                <Trash2 className="h-3.5 w-3.5" />
                Clear
              </Button>
            ) : null}
          </div>

          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-3">
            {messages.length === 0 ? (
              <p className="text-sm text-sidebar-muted">Ask anything — your prompts stay in this thread.</p>
            ) : null}
            {messages.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => m.role === "assistant" && replayTurn(m.id)}
                className={cn(
                  "block w-full rounded-lg px-3 py-2 text-left text-sm transition-colors",
                  m.role === "user"
                    ? "ml-6 bg-primary text-primary-foreground"
                    : "mr-6 bg-white/10 hover:bg-sidebar-accent",
                  m.id === activeTurnId && m.role === "assistant" && "ring-1 ring-primary",
                )}
              >
                <div className="text-[10px] uppercase tracking-wide opacity-70">
                  {m.role === "user" ? "You" : m.domain?.replace(/_/g, " ") ?? "Assistant"}
                </div>
                <div className="mt-0.5">{m.text}</div>
              </button>
            ))}
            {busy ? (
              <div className="mr-6 rounded-lg bg-white/10 px-3 py-2 text-sm text-sidebar-muted">Thinking…</div>
            ) : null}
            <div ref={chatEndRef} />
          </div>

          <div className="shrink-0 space-y-3 border-t border-sidebar-border px-5 py-3">
            <div className="flex gap-2">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void submit();
                  }
                }}
                rows={2}
                disabled={busy}
                className="resize-none border-sidebar-border bg-white/5 text-sidebar-foreground placeholder:text-sidebar-muted"
                placeholder="Ask in natural language…"
              />
              <Button type="button" size="icon" disabled={busy} onClick={() => void submit()} aria-label="Send">
                <Send />
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {EXAMPLES.slice(0, 4).map((ex) => (
                <Button
                  key={ex}
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={busy}
                  onClick={() => void submit(ex)}
                  className="h-auto whitespace-normal border-sidebar-border bg-transparent px-2 py-1 text-[10px] text-sidebar-foreground hover:bg-sidebar-accent"
                >
                  {ex.length > 28 ? `${ex.slice(0, 28)}…` : ex}
                </Button>
              ))}
            </div>
          </div>

          <div className="max-h-56 shrink-0 space-y-4 overflow-y-auto border-t border-sidebar-border px-5 py-3">
            <section className="space-y-2">
              <Label className="text-xs font-semibold uppercase tracking-wide text-sidebar-muted">User context</Label>
              <Select
                value={String(userIdx)}
                onValueChange={(value) => setUserIdx(Number(value))}
              >
                <SelectTrigger className="border-sidebar-border bg-white/5 text-sidebar-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {USERS.map((u, i) => (
                    <SelectItem key={u.id} value={String(i)}>
                      {u.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-sidebar-muted">
                role={user.role} · device={device} · locale=en-IN
              </p>
            </section>

            <section>
              <div className="text-xs font-semibold uppercase tracking-wide text-sidebar-muted">Domain detected</div>
              <div className="mt-1 font-mono text-sm text-primary">{domainHint}</div>
            </section>

            <PipelineAnimation stage={stage} />

            <section>
              <div className="text-xs font-semibold uppercase tracking-wide text-sidebar-muted">Agent activity</div>
              <ol className="mt-2 space-y-1.5 text-sm">
                {activity.length === 0 ? <li className="text-sidebar-muted">Waiting for a prompt…</li> : null}
                {activity.map((a, i) => (
                  <li key={i} className={a.status === "error" ? "text-destructive" : "text-sidebar-foreground"}>
                    {a.status === "error" ? "✕" : "✓"} {a.detail}
                  </li>
                ))}
              </ol>
            </section>

            <section>
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-sidebar-muted">
                Network inspector
              </div>
              <div className="space-y-1">
                {inspector.slice(0, 20).map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setOpenMsg(m.id)}
                    className="block w-full rounded-md bg-white/5 px-2 py-1.5 text-left transition-colors hover:bg-sidebar-accent"
                  >
                    <div className="flex justify-between font-mono text-[11px] text-primary">
                      <span>{m.type}</span>
                      <span className="text-sidebar-muted">{m.ts.slice(11, 19)}</span>
                    </div>
                    <div className="text-[11px] text-sidebar-muted">{m.surfaceId || "—"}</div>
                  </button>
                ))}
              </div>
            </section>
          </div>
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center justify-between border-b border-border bg-card px-6 py-3">
          <div className="text-sm text-muted-foreground">Dynamic A2UI canvas</div>
          <div className="flex gap-2">
            <Button
              type="button"
              variant={device === "desktop" ? "default" : "ghost"}
              size="icon"
              onClick={() => setDevice("desktop")}
              aria-label="Desktop preview"
            >
              <Monitor />
            </Button>
            <Button
              type="button"
              variant={device === "mobile" ? "default" : "ghost"}
              size="icon"
              onClick={() => setDevice("mobile")}
              aria-label="Mobile preview"
            >
              <Smartphone />
            </Button>
            <Button
              type="button"
              variant={showArch ? "default" : "ghost"}
              size="icon"
              onClick={() => setShowArch((v) => !v)}
              aria-label="Architecture view"
            >
              <Boxes />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto bg-background p-6">
          {showArch ? (
            <ArchitectureView stage={stage} />
          ) : (
            <div
              className={
                device === "mobile"
                  ? "mx-auto w-[390px] device-frame bg-background"
                  : "mx-auto max-w-4xl"
              }
            >
              <div className={device === "mobile" ? "min-h-[680px] bg-background p-4" : "px-1 py-2"}>
                {activeSurfaceId ? <A2UIRenderer surfaceId={activeSurfaceId} /> : <A2UIRenderer surfaceId="" />}
              </div>
            </div>
          )}
        </div>
      </main>

      <Dialog open={Boolean(openMsg)} onOpenChange={(open) => !open && setOpenMsg(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-mono text-sm">{openInspector?.type ?? "Message"}</DialogTitle>
            <DialogDescription>{openInspector?.surfaceId || "No surface"}</DialogDescription>
          </DialogHeader>
          <pre className="max-h-[50vh] overflow-auto rounded-md bg-muted p-3 text-xs text-foreground">
            {JSON.stringify(openInspector?.payload, null, 2)}
          </pre>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function PipelineAnimation({ stage }: { stage: string }) {
  return (
    <section>
      <div className="text-xs font-semibold uppercase tracking-wide text-sidebar-muted">Live pipeline</div>
      <div className="mt-2 flex flex-col gap-1">
        {PIPELINE.map((s) => (
          <div
            key={s}
            className={cn(
              "rounded-md px-2 py-1 font-mono text-[11px]",
              stage === s ? "bg-sidebar-accent text-primary" : "text-sidebar-muted",
            )}
          >
            {s}
          </div>
        ))}
      </div>
    </section>
  );
}

function ArchitectureView({ stage }: { stage: string }) {
  const nodes = [
    "USER",
    "INTENT ROUTER",
    "DOMAIN AGENTS",
    "TOOLS / APIS",
    "A2UI GENERATOR",
    "SSE",
    "A2UI RUNTIME",
    "COMPONENT CATALOG",
    "REACT",
  ];
  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <CardTitle>Architecture</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-2">
        {nodes.map((n) => (
          <div key={n} className="flex flex-col items-center">
            <div
              className={cn(
                "rounded-md px-4 py-2 text-sm font-semibold",
                stage.replace(/_/g, " ") === n || stage === n.replace(/ /g, "_")
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-foreground",
              )}
            >
              {n}
            </div>
            <div className="h-4 w-px bg-border" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
