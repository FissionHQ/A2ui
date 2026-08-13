import { describe, expect, it } from "vitest";
import { getPointer, parsePointer, setPointer } from "../a2ui/jsonPointer";
import { validateMessage, CatalogError } from "../a2ui/validate";
import { AppCatalog } from "../catalog/AppCatalog";

describe("json pointer", () => {
  it("reads and writes", () => {
    const doc = { weather: { currentTemperature: 31 } };
    expect(getPointer(doc, "/weather/currentTemperature")).toBe(31);
    const next = setPointer(doc, "/news/articles/0/title", "Hello") as { news: { articles: { title: string }[] } };
    expect(next.news.articles[0].title).toBe("Hello");
  });
  it("rejects invalid pointers", () => {
    expect(() => parsePointer("weather")).toThrow(/Invalid JSON Pointer/);
  });
});

describe("catalog", () => {
  it("rejects unknown components", () => {
    expect(() =>
      validateMessage({
        version: "v1.0",
        updateComponents: {
          surfaceId: "x",
          components: [{ id: "root", component: "SuperFancyWidget" }],
        },
      }),
    ).toThrow(CatalogError);
  });
  it("registers weather card", () => {
    expect(AppCatalog.WeatherCard).toBeTruthy();
  });
});
