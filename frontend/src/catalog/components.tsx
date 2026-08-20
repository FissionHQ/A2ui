import React, { useId, type ReactNode } from "react";
import {
  CloudSun,
  Newspaper,
  Plane,
  TrendingUp,
  ShoppingBag,
  Landmark,
  Headphones,
  Star,
  Smartphone,
  Laptop,
  Watch,
  Footprints,
  Hotel,
  GitCompare,
  Film,
  Swords,
  Laugh,
  Skull,
  Heart,
  Rocket,
  Sparkles,
  BookOpen,
  Search,
  Theater,
  Music,
} from "lucide-react";
import { Badge as UiBadge } from "@/components/ui/badge";
import { Button as UiButton } from "@/components/ui/button";
import {
  Table as UiTable,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow as UiTableRow,
} from "@/components/ui/table";
import { Tabs as UiTabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

type P = Record<string, unknown> & { children?: ReactNode; onAction?: () => void };

function text(v: unknown, fallback = ""): string {
  if (v == null) return fallback;
  if (typeof v === "object") return fallback;
  return String(v);
}

function num(v: unknown): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export function Page({ children }: P) {
  return <div className="flex flex-col gap-6 animate-fade-in-up">{children}</div>;
}

export function Card({ children }: P) {
  return <div className="flex flex-col gap-4 rounded-2xl border border-white/70 bg-card/80 p-4 shadow-[0_18px_50px_-30px_rgba(15,23,42,.35)] backdrop-blur-xl">{children}</div>;
}

export function MetricCard(p: P) {
  const delta = num(p.delta);
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border/70 bg-card/90 px-5 py-4 shadow-[0_14px_40px_-28px_rgba(15,23,42,.45)] transition duration-300 hover:-translate-y-0.5 hover:shadow-lg">
      <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-primary via-amber-400 to-transparent opacity-80" />
      <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">{text(p.title)}</div>
      <div className="mt-2 text-3xl font-semibold tracking-[-0.04em] text-foreground">
        {text(p.value, "—")}
        {p.unit ? <span className="ml-1 text-sm font-medium text-muted-foreground">{text(p.unit)}</span> : null}
      </div>
      {delta != null ? (
        <div className={cn("mt-2 inline-flex rounded-full px-2 py-0.5 text-xs font-semibold", delta >= 0 ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive")}>
          {delta >= 0 ? "+" : ""}
          {delta}%
        </div>
      ) : null}
    </div>
  );
}

export function Alert(p: P) {
  const variant = text(p.variant, "info");
  if (variant === "info") {
    return (
      <div>
        <h2 className="text-2xl font-semibold capitalize tracking-tight text-foreground">{text(p.title)}</h2>
        <p className="mt-1 text-sm text-muted-foreground">{text(p.message)}</p>
      </div>
    );
  }
  const tones: Record<string, string> = {
    warning: "bg-warning/10 text-foreground ring-1 ring-warning/30",
    danger: "bg-destructive/10 text-foreground ring-1 ring-destructive/30",
  };
  return (
    <div className={cn("rounded-xl px-4 py-3", tones[variant] || tones.warning)}>
      <div className="font-semibold">{text(p.title)}</div>
      <div className="mt-1 whitespace-pre-wrap text-sm">{text(p.message)}</div>
    </div>
  );
}

export function Button(p: P) {
  const variant = text(p.variant, "primary");
  return (
    <UiButton type="button" variant={variant === "danger" ? "destructive" : "default"} onClick={p.onAction}>
      {text(p.label, "Continue")}
      {p.children}
    </UiButton>
  );
}

export function CompareButton(p: P) {
  const selected = Boolean(p.selected);
  return (
    <UiButton type="button" size="sm" variant={selected ? "default" : "outline"} onClick={p.onAction}>
      <GitCompare />
      {selected ? "Added" : text(p.label, "Compare")}
    </UiButton>
  );
}

export const PayButton = Button;
export const RefundButton = Button;

export function Badge(p: P) {
  return <UiBadge>{text(p.children ?? p.label ?? p.badge)}</UiBadge>;
}

export function StatusChip(p: P) {
  const tone = text(p.tone, "info");
  const variant =
    tone === "up" ? "success" : tone === "down" ? "destructive" : tone === "warning" ? "warning" : "secondary";
  return <UiBadge variant={variant}>{text(p.label)}</UiBadge>;
}

export function Image(p: P) {
  const src = text(p.src ?? p.imageUrl);
  if (!src || src.startsWith("javascript:")) {
    return <div className="flex h-28 w-full items-center justify-center rounded-xl bg-gradient-to-br from-primary/15 via-amber-100 to-muted"><Newspaper className="h-8 w-8 text-primary/70" /></div>;
  }
  if (!src.startsWith("https:") && !src.startsWith("/")) {
    return <div className="h-28 w-full rounded-xl bg-muted" />;
  }
  return <img src={src} alt={text(p.alt, "")} className="h-28 w-full rounded-xl object-cover" />;
}

export function Chart(p: P) {
  const series = Array.isArray(p.series) ? (p.series as Array<{ label?: string; value?: number }>) : [];
  const gradientId = useId().replace(/:/g, "");
  const values = series.map((s) => Number(s.value)).filter(Number.isFinite);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 1;
  const range = Math.max(max - min, Math.abs(max) * 0.01, 1);
  const points = series.map((s, i) => {
    const x = series.length <= 1 ? 360 : 28 + (i / (series.length - 1)) * 664;
    const y = 184 - ((Number(s.value) - min) / range) * 140;
    return { x, y, value: Number(s.value), label: s.label };
  });
  const line = points.map((point) => `${point.x},${point.y}`).join(" ");
  const area = points.length ? `28,190 ${line} 692,190` : "";
  return (
    <div className="relative overflow-hidden rounded-3xl border border-border/60 bg-[linear-gradient(145deg,rgba(255,255,255,.98),rgba(255,247,237,.84))] p-5 shadow-[0_24px_70px_-40px_rgba(242,80,17,.5)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">Market trajectory</div>
          <div className="mt-1 text-lg font-semibold text-foreground">{text(p.title)}</div>
        </div>
        {values.length ? <div className="rounded-full bg-foreground px-3 py-1 text-xs font-semibold text-background">{values.at(-1)?.toLocaleString("en-IN")}</div> : null}
      </div>
      {points.length ? (
        <div className="mt-3">
          <svg viewBox="0 0 720 210" role="img" aria-label={`${text(p.title)} chart`} className="h-auto w-full overflow-visible">
            <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--primary)" stopOpacity=".28"/><stop offset="100%" stopColor="var(--primary)" stopOpacity="0"/></linearGradient></defs>
            {[50, 95, 140, 185].map((y) => <line key={y} x1="28" y1={y} x2="692" y2={y} stroke="var(--border)" strokeDasharray="4 7" />)}
            <polygon points={area} fill={`url(#${gradientId})`} />
            <polyline points={line} fill="none" stroke="var(--primary)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
            {points.map((point, i) => <circle key={i} cx={point.x} cy={point.y} r="5" fill="var(--card)" stroke="var(--primary)" strokeWidth="3" />)}
          </svg>
          <div className="-mt-2 flex justify-between px-1 text-[10px] font-medium text-muted-foreground">
            {series.map((s, i) => <span key={i}>{s.label}</span>)}
          </div>
        </div>
      ) : <div className="mt-4 rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">Chart data is unavailable.</div>}
    </div>
  );
}

export const ForecastChart = Chart;

export function Tabs(p: P) {
  const tabs = Array.isArray(p.tabs) ? (p.tabs as Array<{ id: string; label: string }>) : [];
  const value = text(p.value) || tabs[0]?.id;
  return (
    <UiTabs value={value}>
      <TabsList>
        {tabs.map((t) => (
          <TabsTrigger key={t.id} value={t.id} onClick={p.onAction}>
            {t.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </UiTabs>
  );
}

export function Progress(p: P) {
  const v = Math.min(100, Math.max(0, num(p.value) || 0));
  return (
    <div className="h-2 overflow-hidden rounded-full bg-muted">
      <div className="h-full bg-primary" style={{ width: `${v}%` }} />
    </div>
  );
}

export function Timeline(p: P) {
  const items = Array.isArray(p.items) ? (p.items as Array<{ title: string; detail: string }>) : [];
  return (
    <ol className="space-y-3 border-l-2 border-primary/30 pl-4">
      {items.map((it, i) => (
        <li key={i}>
          <div className="text-sm font-semibold text-foreground">{it.title}</div>
          <div className="text-xs text-muted-foreground">{it.detail}</div>
        </li>
      ))}
    </ol>
  );
}

export function List({ children }: P) {
  return <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">{children}</div>;
}

export function NewsList({ children }: P) {
  return <div className="flex flex-col gap-3">{children}</div>;
}

export function ProductList({ children }: P) {
  return <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">{children}</div>;
}

export function ListItem({ children }: P) {
  return <div className="rounded-xl bg-card p-3 shadow-sm ring-1 ring-border">{children}</div>;
}

export function Table(p: P) {
  const columns = Array.isArray(p.columns) ? (p.columns as string[]) : [];
  const rows = Array.isArray(p.rows)
    ? (p.rows as Array<Record<string, unknown>>)
    : Array.isArray(p.movers)
      ? (p.movers as Array<Record<string, unknown>>)
      : [];
  const dataRows = rows.length
    ? rows
    : Array.isArray((p as { rowsData?: unknown }).rowsData)
      ? ((p as { rowsData: Array<Record<string, unknown>> }).rowsData)
      : [];
  return (
    <div className="overflow-hidden rounded-xl bg-card shadow-sm ring-1 ring-border">
      <UiTable>
        <TableHeader>
          <UiTableRow>
            {columns.map((c) => (
              <TableHead key={c}>{c}</TableHead>
            ))}
          </UiTableRow>
        </TableHeader>
        <TableBody>
          {dataRows.map((row, i) => (
            <UiTableRow key={i}>
              {columns.map((c) => (
                <TableCell key={c}>{text(row[c])}</TableCell>
              ))}
            </UiTableRow>
          ))}
        </TableBody>
      </UiTable>
    </div>
  );
}
export function TableRow({ children }: P) {
  return <tr>{children}</tr>;
}

export function WeatherCard(p: P) {
  return (
    <div className="flex items-center gap-4 rounded-2xl bg-primary p-6 text-primary-foreground shadow-md">
      <CloudSun className="h-14 w-14 shrink-0" />
      <div>
        <div className="text-sm text-primary-foreground/80">
          {text(p.location)} · {text(p.date)}
        </div>
        <div className="text-4xl font-semibold tracking-tight">{text(p.temperature)}°</div>
        <div className="text-sm">{text(p.condition)}</div>
      </div>
    </div>
  );
}

export function NewsCard(p: P) {
  return (
    <article className="group flex gap-4 rounded-2xl border border-border/60 bg-card/90 p-4 shadow-[0_14px_45px_-32px_rgba(15,23,42,.5)] transition duration-300 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg">
      <div className="w-24 shrink-0 overflow-hidden rounded-xl">
        <Image imageUrl={p.imageUrl} />
      </div>
      <div className="min-w-0">
        <Badge badge={p.badge} />
        <h3 className="mt-2 font-semibold leading-snug text-foreground transition-colors group-hover:text-primary">{text(p.title)}</h3>
        <p className="mt-1 line-clamp-2 text-sm leading-relaxed text-muted-foreground">{text(p.summary)}</p>
        <div className="mt-1 text-xs text-muted-foreground">{text(p.source)}</div>
        <UiButton type="button" variant="link" className="mt-2 h-auto px-0 text-xs" onClick={p.onAction}>
          Read story →
        </UiButton>
      </div>
    </article>
  );
}

export function TravelCard(p: P) {
  return (
    <div className="rounded-2xl bg-sidebar p-6 text-sidebar-foreground shadow-md">
      <div className="flex items-center gap-2 text-primary">
        <Plane className="h-4 w-4" /> Weekend plan
      </div>
      <h2 className="mt-2 text-2xl font-semibold">{text(p.destination)}</h2>
      <p className="text-sm text-sidebar-muted">{text(p.dates)}</p>
      <p className="mt-2 text-sm">{text(p.summary)}</p>
    </div>
  );
}

function OfferTile(p: P & { kind: string; icon: ReactNode }) {
  return (
    <div className="rounded-xl bg-card p-4 shadow-sm ring-1 ring-border">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground">
        {p.icon}
        {p.kind}
      </div>
      <div className="mt-1 font-semibold text-foreground">{text(p.title)}</div>
      <div className="text-sm text-muted-foreground">{text(p.detail)}</div>
      <div className="mt-2 text-sm font-medium text-primary">₹{Number(p.price).toLocaleString("en-IN")}</div>
    </div>
  );
}

export function FlightCard(p: P) {
  return <OfferTile {...p} kind="Flight" icon={<Plane className="h-3.5 w-3.5" />} />;
}

export function HotelCard(p: P) {
  return <OfferTile {...p} kind="Hotel" icon={<Hotel className="h-3.5 w-3.5" />} />;
}

export function MarketCard(p: P) {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-[radial-gradient(circle_at_top_right,rgba(251,146,60,.35),transparent_38%),linear-gradient(135deg,#18181b,#292524)] p-6 text-white shadow-2xl">
      <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full border border-white/10" />
      <div className="relative">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-orange-200">Live market pulse</div>
        <div className="flex items-center gap-3 text-2xl font-semibold tracking-tight">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white shadow-lg shadow-primary/25"><TrendingUp className="h-5 w-5" /></span>
          {text(p.title)}
        </div>
        <div className="mt-2 text-xs text-white/55">Updated {text(p.asOf)}</div>
      </div>
    </div>
  );
}

function ProductGlyph({ title }: { title: string }) {
  const t = title.toLowerCase();
  const Icon =
    /headphone|earbud|earphone/.test(t)
      ? Headphones
      : /phone|galaxy|iphone|pixel|oneplus|motorola|nord/.test(t)
        ? Smartphone
        : /laptop|macbook|vivobook|ideapad/.test(t)
          ? Laptop
          : /shoe|nike|adidas/.test(t)
            ? Footprints
            : /watch/.test(t)
              ? Watch
              : ShoppingBag;
  return <Icon className="h-6 w-6 text-primary" />;
}

export function ProductCard(p: P) {
  const selected = Boolean(p.selected);
  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-xl bg-card p-4 shadow-sm ring-1 transition-shadow",
        selected ? "ring-2 ring-primary shadow-md" : "ring-border",
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
          <ProductGlyph title={text(p.title)} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-semibold leading-snug text-foreground">{text(p.title)}</div>
          <Rating value={p.rating} />
        </div>
      </div>
      <div className="flex items-center justify-between gap-2">
        <Price value={p.price} />
        {p.children}
      </div>
    </div>
  );
}

export function CompareTray(p: P) {
  const items = Array.isArray(p.items) ? (p.items as Array<Record<string, unknown>>) : [];
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
        Select 2 or 3 products with Compare to see them side by side.
      </div>
    );
  }
  return (
    <div className="rounded-xl bg-card p-4 shadow-sm ring-1 ring-primary/20">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="font-semibold text-foreground">Compare ({items.length})</div>
        <UiButton type="button" variant="ghost" size="sm" onClick={p.onAction}>
          Clear
        </UiButton>
      </div>
      <div className={cn("grid gap-3", items.length === 1 ? "grid-cols-1" : items.length === 2 ? "grid-cols-2" : "grid-cols-3")}>
        {items.map((item, i) => (
          <div key={i} className="rounded-lg bg-muted/60 p-3">
            <div className="text-sm font-semibold text-foreground">{text(item.title)}</div>
            <Rating value={item.rating} />
            <Price value={item.price} />
          </div>
        ))}
      </div>
    </div>
  );
}

export function Rating(p: P) {
  const v = num(p.value) ?? 0;
  return (
    <div className="flex items-center gap-1 text-warning">
      <Star className="h-3.5 w-3.5 fill-current" />
      <span className="text-xs text-muted-foreground">{v.toFixed(1)}</span>
    </div>
  );
}

export function Price(p: P) {
  const v = num(p.value) ?? num(p.price) ?? 0;
  return <div className="font-semibold text-foreground">₹{v.toLocaleString("en-IN")}</div>;
}

export function InvoiceTable(p: P) {
  const rows = Array.isArray(p.rows) ? (p.rows as Array<Record<string, unknown>>) : [];
  return (
    <div className="overflow-hidden rounded-xl bg-card shadow-sm ring-1 ring-border">
      <UiTable>
        <TableHeader>
          <UiTableRow>
            {["Invoice", "Customer", "Amount", "Due", "Status", ""].map((c) => (
              <TableHead key={c}>{c}</TableHead>
            ))}
          </UiTableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, i) => (
            <UiTableRow key={i}>
              <TableCell className="font-medium">{text(row.id)}</TableCell>
              <TableCell>{text(row.customer)}</TableCell>
              <TableCell>₹{Number(row.amount || 0).toLocaleString("en-IN")}</TableCell>
              <TableCell>{text(row.due)}</TableCell>
              <TableCell>
                <StatusChip label={row.status} tone={row.status === "overdue" ? "warning" : "info"} />
              </TableCell>
              <TableCell>
                <Button label="Pay" onAction={p.onAction} />
              </TableCell>
            </UiTableRow>
          ))}
        </TableBody>
      </UiTable>
    </div>
  );
}

export function MilestoneCard(p: P) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-xl bg-card p-4 shadow-sm ring-1 ring-border">
      <div>
        <div className="text-xs uppercase tracking-wide text-muted-foreground">Milestone</div>
        <div className="text-lg font-semibold text-foreground">{text(p.title)}</div>
        <div className="text-sm text-muted-foreground">{text(p.client)}</div>
        <div className="mt-2">
          <StatusChip label={p.status} tone="up" />
        </div>
      </div>
      <div className="text-right">
        <Price value={p.amount} />
        <div className="mt-2">
          <Button label="Release" onAction={p.onAction} />
        </div>
      </div>
    </div>
  );
}

export function OrderCard(p: P) {
  return (
    <div className="rounded-xl bg-card p-4 shadow-sm ring-1 ring-border">
      <div className="text-xs uppercase tracking-wide text-muted-foreground">Order {text(p.orderId)}</div>
      <div className="text-lg font-semibold text-foreground">{text(p.item)}</div>
      <div className="text-sm text-muted-foreground">{text(p.eta)}</div>
    </div>
  );
}

void Newspaper;
void Landmark;

// --- Generic item card/list — reuse for any domain that has icon+title+meta+rating ---

export function ItemList({ children, columns }: P & { columns?: number }) {
  const cols = Number(columns) || 2;
  const cls = cols === 1 ? "grid-cols-1" : cols === 3 ? "grid-cols-1 sm:grid-cols-3" : "grid-cols-1 sm:grid-cols-2";
  return <div className={`grid gap-3 ${cls}`}>{children}</div>;
}

export function ItemCard(p: P) {
  const rating = num(p.rating) ?? null;
  const ICONS: Record<string, React.ElementType> = {
    film: Film, plane: Plane, star: Star,
    swords: Swords, laugh: Laugh, skull: Skull, heart: Heart,
    rocket: Rocket, sparkles: Sparkles, "book-open": BookOpen,
    search: Search, theater: Theater, music: Music,
  };
  const iconKey = (p.icon != null && typeof p.icon !== "object" ? String(p.icon) : "film").toLowerCase();
  const Icon = ICONS[iconKey] ?? Film;
  return (
    <div className="flex gap-4 rounded-2xl border border-border/60 bg-card/90 p-4 shadow-[0_14px_45px_-32px_rgba(15,23,42,.5)] transition duration-300 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg">
      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary/10">
        <Icon className="h-7 w-7 text-primary" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="font-semibold leading-snug text-foreground">{text(p.title)}</div>
        <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          {p.subtitle  && <span>{text(p.subtitle)}</span>}
          {p.year      && <span>{text(p.year)}</span>}
          {p.badge     && <UiBadge variant="secondary">{text(p.badge)}</UiBadge>}
          {p.genre     && <UiBadge variant="secondary">{text(p.genre)}</UiBadge>}
        </div>
        {p.meta && <div className="mt-1 text-xs text-muted-foreground">{text(p.meta)}</div>}
        {p.director && <div className="mt-1 text-xs text-muted-foreground">Dir. {text(p.director)}</div>}
        {rating !== null && (
          <div className="mt-1 flex items-center gap-1 text-warning">
            <Star className="h-3.5 w-3.5 fill-current" />
            <span className="text-xs font-semibold text-foreground">{rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// MovieCard and MovieList removed — use ItemCard and ItemList directly
