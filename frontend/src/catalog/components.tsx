import type { ReactNode } from "react";
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
  return <div className="flex flex-col gap-5">{children}</div>;
}

export function Card({ children }: P) {
  return <div className="flex flex-col gap-4">{children}</div>;
}

export function MetricCard(p: P) {
  const delta = num(p.delta);
  return (
    <div className="rounded-xl bg-card px-4 py-3 shadow-sm ring-1 ring-border">
      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{text(p.title)}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
        {text(p.value, "—")}
        {p.unit ? <span className="ml-1 text-sm font-medium text-muted-foreground">{text(p.unit)}</span> : null}
      </div>
      {delta != null ? (
        <div className={cn("text-sm font-medium", delta >= 0 ? "text-success" : "text-destructive")}>
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
    return <div className="h-28 w-full rounded-xl bg-muted" />;
  }
  if (!src.startsWith("https:") && !src.startsWith("/")) {
    return <div className="h-28 w-full rounded-xl bg-muted" />;
  }
  return <img src={src} alt={text(p.alt, "")} className="h-28 w-full rounded-xl object-cover" />;
}

export function Chart(p: P) {
  const series = Array.isArray(p.series) ? (p.series as Array<{ label?: string; value?: number }>) : [];
  const max = Math.max(1, ...series.map((s) => Number(s.value) || 0));
  return (
    <div className="rounded-xl bg-card p-4 shadow-sm ring-1 ring-border">
      <div className="mb-3 text-sm font-medium text-muted-foreground">{text(p.title)}</div>
      <div className="flex h-28 items-end gap-2">
        {series.map((s, i) => (
          <div key={i} className="flex flex-1 flex-col items-center gap-1">
            <div
              className="w-full rounded-t-md bg-primary/80"
              style={{ height: `${((Number(s.value) || 0) / max) * 100}%` }}
            />
            <span className="text-[10px] text-muted-foreground">{s.label}</span>
          </div>
        ))}
      </div>
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
    <article className="flex gap-3 rounded-xl bg-card p-3 shadow-sm ring-1 ring-border">
      <div className="w-24 shrink-0">
        <Image imageUrl={p.imageUrl} />
      </div>
      <div className="min-w-0">
        <Badge badge={p.badge} />
        <h3 className="mt-1 font-semibold text-foreground">{text(p.title)}</h3>
        <p className="text-sm text-muted-foreground">{text(p.summary)}</p>
        <div className="mt-1 text-xs text-muted-foreground">{text(p.source)}</div>
        <UiButton type="button" variant="link" className="mt-1 h-auto px-0" onClick={p.onAction}>
          Open
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
    <div className="flex items-center justify-between">
      <div>
        <div className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <TrendingUp className="h-5 w-5 text-primary" />
          {text(p.title)}
        </div>
        <div className="text-xs text-muted-foreground">{text(p.asOf)}</div>
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
