export type A2UIMessage =
  | { version: "v1.0"; createSurface: CreateSurface }
  | { version: "v1.0"; updateComponents: UpdateComponents }
  | { version: "v1.0"; updateDataModel: UpdateDataModel }
  | { version: "v1.0"; deleteSurface: { surfaceId: string } }
  | { version: "v1.0"; actionResponse: { actionId: string; value?: unknown; error?: { code: string; message: string } } }
  | { version: "demo"; agentActivity: { step: string; detail: string; status?: string } }
  | { version: "demo"; pipeline: { stage: string } };

export type CreateSurface = {
  surfaceId: string;
  catalogId?: string;
  sendDataModel?: boolean;
  components?: A2UIComponent[];
  dataModel?: unknown;
};

export type UpdateComponents = {
  surfaceId: string;
  components: A2UIComponent[];
};

export type UpdateDataModel = {
  surfaceId: string;
  path?: string;
  value: unknown;
};

export type Bound<T> = T | { path: string };

export type A2UIComponent = {
  id: string;
  component: string;
  catalogId?: string;
  child?: string;
  children?: string[] | { componentId: string; path: string };
  action?: {
    functionCall?: { call: string; args?: Record<string, unknown> };
    event?: { name: string; context?: Record<string, unknown> };
  };
  [key: string]: unknown;
};

export type SurfaceState = {
  catalog: string;
  components: Record<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
  status: "creating" | "ready" | "error" | "deleted";
};

export const CATALOG_ID = "AppCatalog";

export const COMPONENT_NAMES = [
  "Page",
  "Card",
  "MetricCard",
  "List",
  "ListItem",
  "Table",
  "TableRow",
  "Badge",
  "StatusChip",
  "Button",
  "Image",
  "Chart",
  "Tabs",
  "Progress",
  "Timeline",
  "Alert",
  "WeatherCard",
  "NewsCard",
  "TravelCard",
  "MarketCard",
  "ProductCard",
  "InvoiceTable",
  "MilestoneCard",
  "ForecastChart",
  "NewsList",
  "FlightCard",
  "HotelCard",
  "ProductList",
  "Rating",
  "Price",
  "CompareButton",
  "CompareTray",
  "PayButton",
  "OrderCard",
  "RefundButton",
] as const;

export const LOCAL_FUNCTIONS = new Set([
  "changeTab",
  "filterList",
  "sortList",
  "searchList",
  "toggleCompare",
  "clearCompare",
]);
