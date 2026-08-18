import type { ReactNode } from "react";
import { AppCatalog } from "../catalog/AppCatalog";
import { getPointer } from "./jsonPointer";
import type { A2UIComponent } from "./types";
import { useA2UIStore } from "../store/a2uiStore";
import { dispatchAction } from "./actions";

function resolve(value: unknown, data: unknown, index?: number): unknown {
  if (value && typeof value === "object" && "path" in (value as object)) {
    let path = String((value as { path: string }).path);
    if (typeof index === "number") path = path.replace("/@index/", `/${index}/`).replace("/@index", `/${index}`);
    return getPointer(data, path);
  }
  return value;
}

function resolveProps(comp: A2UIComponent, data: unknown, index?: number): Record<string, unknown> {
  const skip = new Set(["id", "component", "catalogId", "children", "child", "action", "accessibility"]);
  const props: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(comp)) {
    if (skip.has(k)) continue;
    props[k] = resolve(v, data, index);
  }
  if (comp.component === "Table") {
    const raw = comp.rowsPath;
    const rowsPath =
      typeof raw === "string"
        ? getPointer(data, raw)
        : raw
          ? resolve(raw, data, index)
          : getPointer(data, "/market/movers");
    if (Array.isArray(rowsPath)) props.rowsData = rowsPath;
  }
  if (comp.component === "InvoiceTable") {
    const rows = getPointer(data, "/fintech/invoices");
    if (Array.isArray(rows)) props.rows = rows;
  }
  if (comp.component === "Chart" || comp.component === "ForecastChart") {
    props.series = resolve(comp.series, data, index);
  }
  if (comp.component === "Timeline" || comp.component === "CompareTray") {
    props.items = resolve(comp.items, data, index);
  }
  if (comp.component === "CompareButton" || comp.component === "ProductCard") {
    const compared = getPointer(data, "/shopping/compared");
    const title =
      typeof index === "number" ? getPointer(data, `/shopping/products/${index}/title`) : props.title;
    props.selected =
      Array.isArray(compared) &&
      compared.some((p) => p && typeof p === "object" && (p as { title?: unknown }).title === title);
  }
  return props;
}

function Node({
  id,
  components,
  data,
  surfaceId,
  index,
}: {
  id: string;
  components: Record<string, A2UIComponent>;
  data: unknown;
  surfaceId: string;
  index?: number;
}) {
  const comp = components[id];
  if (!comp) {
    return <div className="rounded-lg border border-dashed border-border p-2 text-xs text-muted-foreground">Missing component: {id}</div>;
  }
  const entry = AppCatalog[comp.component];
  if (!entry) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-foreground">
        <div className="font-semibold">Unsupported A2UI component:</div>
        <div className="font-mono">{comp.component}</div>
      </div>
    );
  }
  const Cmp = entry.component;
  const props = resolveProps(comp, data, index);
  const kids: string[] | { componentId: string; path: string } | undefined = comp.children as never;
  let childNodes: ReactNode = null;
  if (Array.isArray(kids)) {
    childNodes = kids.map((cid) => (
      <Node key={cid} id={cid} components={components} data={data} surfaceId={surfaceId} />
    ));
  } else if (kids && typeof kids === "object" && "componentId" in kids) {
    const arr = getPointer(data, kids.path);
    const items = Array.isArray(arr) ? arr : [];
    childNodes = items.map((_, i) => (
      <Node key={`${kids.componentId}-${i}`} id={kids.componentId} components={components} data={data} surfaceId={surfaceId} index={i} />
    ));
  } else if (comp.child) {
    childNodes = <Node id={comp.child} components={components} data={data} surfaceId={surfaceId} />;
  }
  return (
    <Cmp
      {...props}
      onAction={() => dispatchAction(comp, surfaceId, data, index)}
    >
      {childNodes}
    </Cmp>
  );
}

export default function A2UIRenderer({ surfaceId }: { surfaceId: string }) {
  const surface = useA2UIStore((s) => s.surfaces[surfaceId]);
  const error = useA2UIStore((s) => s.canvasError);
  if (error) {
    return (
      <div className="whitespace-pre-wrap rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-foreground">
        {error}
      </div>
    );
  }
  if (!surface) {
    return (
      <div className="flex h-full min-h-[520px] flex-col items-center justify-center text-center text-muted-foreground">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-[1.75rem] bg-gradient-to-br from-primary to-orange-400 text-2xl font-bold text-white shadow-2xl shadow-primary/25">A2</div>
        <p className="text-3xl font-semibold tracking-[-0.04em] text-foreground">What should we explore?</p>
        <p className="mt-3 max-w-md text-sm leading-relaxed">Ask naturally. This canvas reshapes itself into market intelligence, weather comparisons, travel plans, shopping tools, and more.</p>
        <div className="mt-7 flex flex-wrap justify-center gap-2 text-xs font-medium"><span className="rounded-full bg-primary/10 px-3 py-1.5 text-primary">Markets</span><span className="rounded-full bg-violet-500/10 px-3 py-1.5 text-violet-600">Weather</span><span className="rounded-full bg-emerald-500/10 px-3 py-1.5 text-emerald-600">Travel</span></div>
      </div>
    );
  }
  return (
    <div key={surfaceId} className="animate-in fade-in-0 duration-300">
      <Node id="root" components={surface.components} data={surface.dataModel} surfaceId={surfaceId} />
    </div>
  );
}
