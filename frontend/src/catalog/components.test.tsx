import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Chart } from "./components";

describe("Chart", () => {
  it("renders market series as a visible line chart", () => {
    const html = renderToStaticMarkup(
      <Chart
        title="NIFTY 30d"
        series={[
          { label: "W1", value: 24120 },
          { label: "W2", value: 24380 },
          { label: "W3", value: 24780 },
        ]}
      />,
    );

    expect(html).toContain('aria-label="NIFTY 30d chart"');
    expect(html).toContain("<polyline");
    expect(html).toContain("24,780");
  });

  it("shows an explicit empty state", () => {
    const html = renderToStaticMarkup(<Chart title="NIFTY 30d" series={[]} />);
    expect(html).toContain("Chart data is unavailable.");
  });
});
