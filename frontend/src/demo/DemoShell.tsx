import { useEffect, useMemo, useRef, useState } from "react";
import { Smartphone, Monitor, Boxes, Trash2, Sparkles, Activity, Bot, UserRound, ArrowUp, Zap } from "lucide-react";
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
import { Toast, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "Compare Hyderabad and Bengaluru weather",
  "What news impacted NIFTY today?",
  "Hotels near Goa airport with breakfast",
  "Plan a weekend trip to Jaipur",
  "Find headphones under ₹10,000.",
  "Show me invoices that need attention.",
  "I want to release my freelancer milestone.",
  "My order is delayed. Can I get a refund?",
  "Show top rated movies",
  "What movies are in theatres now?",
  "Show Jr. NTR movies",
  "Show top rated books",
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
  const [actionNotice, setActionNotice] = useState<{ title: string; description: string } | null>(null);
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

  useEffect(() => {
    const onResult = (event: Event) => {
      const value = (event as CustomEvent<Record<string, unknown>>).detail || {};
      if (value.bookingId) {
        setActionNotice({
          title: `Trip confirmed · ${String(value.bookingId)}`,
          description: String(value.message || "Your mock booking was completed successfully."),
        });
      }
    };
    window.addEventListener("a2ui-action-result", onResult);
    return () => window.removeEventListener("a2ui-action-result", onResult);
  }, []);

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
        : result.routing?.clarificationQuestion
          ? result.routing.clarificationQuestion
        : result.domain
          ? `${result.domain.replace(/_/g, " ")} experience ready`
          : "Experience updated";
      addAssistant({
        text: label,
        domain: result.domain ?? undefined,
        surfaceId: result.surfaceId ?? undefined,
        surface,
        state: result.routing ?? undefined,
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
    <ToastProvider>
    <div className="flex h-full min-h-screen overflow-hidden bg-background text-foreground">
      <aside className="relative flex w-[380px] shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground shadow-2xl xl:w-[400px]">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[radial-gradient(circle_at_top_left,rgba(242,80,17,.2),transparent_62%)]" />
        <header className="relative border-b border-sidebar-border px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-orange-400 text-xs font-bold text-primary-foreground shadow-lg shadow-primary/20">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
                A2UI Adaptive Experience
              </div>
              <h1 className="text-base font-semibold leading-tight tracking-tight">Adaptive intelligence canvas</h1>
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
          <div className="flex items-center justify-between border-b border-sidebar-border px-5 py-3">
            <div>
              <Label className="text-xs font-semibold uppercase tracking-[0.16em] text-sidebar-muted">Conversation</Label>
              <div className="mt-1 flex items-center gap-1.5 text-[10px] text-sidebar-muted"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,.8)]" />Ready to build an experience</div>
            </div>
            {messages.length > 0 ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-8 rounded-full border border-white/5 bg-white/5 px-3 text-xs text-sidebar-muted hover:bg-white/10 hover:text-sidebar-foreground"
                onClick={handleClearHistory}
              >
                <Trash2 className="h-3.5 w-3.5" />
                Clear
              </Button>
            ) : null}
          </div>

          <div className="chat-scroll min-h-0 flex-1 space-y-5 overflow-y-auto px-4 py-5">
            {messages.length === 0 ? (
              <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.055] p-5 shadow-2xl backdrop-blur-xl">
                <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-primary/15 blur-2xl" />
                <div className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-orange-400 text-white shadow-lg shadow-primary/20"><Bot className="h-5 w-5" /></div>
                <div className="relative mt-4 text-lg font-semibold tracking-tight">What can I create for you?</div>
                <p className="relative mt-1 text-sm leading-relaxed text-sidebar-muted">Describe what you need naturally. I’ll turn it into an interactive experience on the canvas.</p>
                <div className="relative mt-4 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-primary"><Zap className="h-3.5 w-3.5" /> Try a prompt below</div>
              </div>
            ) : null}
            {messages.map((m) => {
              const isUser = m.role === "user";
              return (
                <div key={m.id} className={cn("flex items-end gap-2.5", isUser && "justify-end")}>
                  {!isUser ? <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-orange-400 text-white shadow-lg"><Bot className="h-4 w-4" /></div> : null}
                  <button
                    type="button"
                    onClick={() => !isUser && replayTurn(m.id)}
                    className={cn(
                      "max-w-[82%] rounded-2xl px-4 py-3 text-left text-sm leading-relaxed transition-all",
                      isUser
                        ? "rounded-br-md bg-gradient-to-br from-primary to-orange-500 text-primary-foreground shadow-lg shadow-primary/10"
                        : "rounded-bl-md border border-white/10 bg-white/[0.075] text-sidebar-foreground shadow-lg hover:border-primary/30 hover:bg-sidebar-accent",
                      m.id === activeTurnId && !isUser && "ring-1 ring-primary/80",
                    )}
                  >
                    <div className="mb-1 flex items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.14em] opacity-60">
                      <span>{isUser ? "You" : m.domain?.replace(/_/g, " ") ?? "A2 Assistant"}</span>
                      <span>·</span><span>{new Date(m.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                    <div>{m.text}</div>
                  </button>
                  {isUser ? <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/10 text-white"><UserRound className="h-4 w-4" /></div> : null}
                </div>
              );
            })}
            {busy ? (
              <div className="flex items-end gap-2.5"><div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-orange-400 text-white"><Bot className="h-4 w-4" /></div><div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.075] px-4 py-3"><span className="thinking-dot" /><span className="thinking-dot [animation-delay:140ms]" /><span className="thinking-dot [animation-delay:280ms]" /><span className="ml-2 text-xs text-sidebar-muted">Crafting your UI</span></div></div>
            ) : null}
            <div ref={chatEndRef} />
          </div>

          <div className="shrink-0 space-y-3 border-t border-sidebar-border bg-black/20 px-4 py-4 backdrop-blur-xl">
            <div className="group rounded-3xl border border-white/10 bg-white/[0.075] p-2 shadow-[0_18px_45px_-25px_rgba(0,0,0,.8)] transition focus-within:border-primary/50 focus-within:bg-white/[0.09] focus-within:ring-4 focus-within:ring-primary/10">
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
                maxLength={500}
                disabled={busy}
                className="min-h-[70px] resize-none border-0 bg-transparent px-2 py-2 text-[13px] leading-relaxed text-sidebar-foreground shadow-none focus-visible:ring-0 placeholder:text-sidebar-muted"
                placeholder="Describe the experience you want…"
              />
              <Button type="button" size="icon" className="mt-1 shrink-0 rounded-2xl bg-gradient-to-br from-primary to-orange-400 shadow-lg shadow-primary/20 transition hover:-translate-y-0.5" disabled={busy || !text.trim()} onClick={() => void submit()} aria-label="Send">
                <ArrowUp className="h-5 w-5" />
              </Button>
              </div>
              <div className="flex items-center justify-between px-2 pb-0.5 text-[9px] text-sidebar-muted"><span>Enter to send · Shift + Enter for new line</span><span>{text.length}/500</span></div>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none]">
              {EXAMPLES.slice(0, 4).map((ex) => (
                <Button
                  key={ex}
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={busy}
                  onClick={() => void submit(ex)}
                  className="h-7 shrink-0 rounded-full border-white/10 bg-white/[0.055] px-3 text-[10px] text-sidebar-muted hover:border-primary/30 hover:bg-sidebar-accent hover:text-sidebar-foreground"
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

      <main className="relative flex min-w-0 flex-1 flex-col bg-[radial-gradient(circle_at_90%_0%,rgba(251,146,60,.13),transparent_30%),radial-gradient(circle_at_10%_80%,rgba(139,92,246,.08),transparent_28%)]">
        <div className="flex items-center justify-between border-b border-white/70 bg-card/70 px-7 py-4 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary"><Activity className="h-4 w-4" /></span>
            <div><div className="text-sm font-semibold">Live experience</div><div className="text-xs text-muted-foreground">Generated from your intent in real time</div></div>
          </div>
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
        <div className="relative flex-1 overflow-auto p-7 lg:p-10">
          {showArch ? (
            <ArchitectureView stage={stage} />
          ) : (
            <div
              className={
                device === "mobile"
                  ? "mx-auto w-[390px] device-frame bg-background"
                  : "mx-auto max-w-6xl"
              }
            >
              <div className={device === "mobile" ? "min-h-[680px] bg-background p-4" : "rounded-[2rem] border border-white/80 bg-white/45 p-6 shadow-[0_30px_100px_-55px_rgba(15,23,42,.5)] backdrop-blur-sm lg:p-8"}>
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
      <Toast open={Boolean(actionNotice)} onOpenChange={(open) => !open && setActionNotice(null)} variant="success">
        <div>
          <ToastTitle>{actionNotice?.title}</ToastTitle>
          <ToastDescription>{actionNotice?.description}</ToastDescription>
        </div>
      </Toast>
      <ToastViewport />
    </div>
    </ToastProvider>
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
