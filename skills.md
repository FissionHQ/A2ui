---
name: a2ui-adaptive-experience-engine
description: Authoritative implementation specification for the A2UI Adaptive Experience Engine. Use when implementing, extending, or generating this repository from scratch. Covers setup interview, A2UI protocol, catalog-driven domain agents that generate A2UI via a2ui-agent-sdk (A2uiSchemaManager), React renderer, FastAPI SSE backend, security, tests, and demo UX. Follows https://a2ui.org/guides/agent-development/. Do not start coding until the setup questionnaire is answered.
---

# A2UI Adaptive Experience Engine — Implementation Skill

This file is the **authoritative implementation specification**.

It is intended to be given to an AI coding tool such as Cursor, Claude Code, Windsurf, Gemini CLI, Codex, or any other coding agent.

When you receive this file, treat it as the source of truth for generating the complete application.

**Do not start implementing the application until you complete Part 0.**

---

## Part 0 — STOP. Setup interview first.

When an AI coding tool reads this file, it **MUST NOT immediately start coding**.

It must first ask the developer a short setup questionnaire and **wait for answers**.

Do not scaffold the React app.
Do not create the FastAPI server.
Do not generate components.
Do not invent defaults for the LLM provider, model, or enabled domains.

Copy the questionnaire below into the conversation **verbatim**, then stop and wait.

------------------------------------------------------------

A2UI Adaptive Experience Engine Setup

Before implementation, I need a few choices.

1. Which LLM provider do you want to use?

   A. OpenAI
   B. Anthropic
   C. Google Gemini
   D. Azure OpenAI
   E. Local Ollama
   F. Other OpenAI-compatible API

2. Which model?

3. Where should the API key be configured?

Recommended:

    .env.local

Example:

    LLM_API_KEY=your-key-here

4. Which business experiences do you want enabled?

   A. Weather
   B. News
   C. Travel
   D. Market Data
   E. Shopping
   F. Fintech
   G. Customer Support
   H. All

5. Do you want live external APIs or mocked data?

   A. Real APIs
   B. Mock data
   C. Mix

6. Do you want the demo to run:

   A. Localhost
   B. Docker
   C. Both

------------------------------------------------------------

After the developer answers:

- Record the answers in `.env.example` comments and in `README.md`.
- Enable only the selected domains, unless the answer is **H. All**.
- Generate an A2UI-producing domain agent **only** for each chosen business experience (or all seven if **H. All**).
- Every domain agent MUST follow the official [A2UI Agent Development Guide](https://a2ui.org/guides/agent-development/): understand intent → generate A2UI JSON from `AppCatalog` via `A2uiSchemaManager` → validate & stream → handle actions.
- Configure the selected LLM provider through the `LLMProvider` abstraction.
- If no `LLM_API_KEY` will be supplied, still implement **Mock Agent Mode** using the same catalog examples the live agents are prompted with.
- Only then begin generating the application.

If the developer has not answered yet, **stop here**.

---

## 1. Project purpose

Build a Proof-of-Concept called:

**A2UI Adaptive Experience Engine**

This is **one application**, not seven applications.

The UI must dynamically become a weather app, news app, travel app, market app, shopping app, fintech app, or customer support app based on:

- USER INTENT
- USER CONTEXT
- AGENT RESULTS

The system uses the **A2UI (Agent-to-UI) protocol**. Agents never generate React, HTML, JSX, or executable frontend code. Agents emit validated, declarative A2UI messages. The client renders those messages using a fixed, approved component catalog.

### Central demo message

The application must communicate:

```
ONE CODEBASE
ONE RENDERER
ONE COMPONENT CATALOG
MANY BUSINESS EXPERIENCES
```

The UI dynamically becomes:

- Weather App
- News App
- Travel App
- Market App
- Shopping App
- Fintech App
- Customer Support App

without application reload.

### Core demonstration

The application should initially display:

```
What do you want to do?
```

with a natural-language input.

Examples:

- "What's the weather in Hyderabad tomorrow?"
- "Show me today's AI news."
- "Plan a weekend trip to Goa."
- "How is the Indian stock market doing?"
- "Find headphones under ₹10,000."
- "Show me invoices that need attention."
- "I want to release my freelancer milestone."

The system must determine the appropriate business experience and transform the canvas.

---

## 2. The A2UI principle (document this prominently)

This principle must appear in `README.md`, in a comment at the top of the renderer, and in the Architecture view.

The agent controls:

```
WHICH APPROVED COMPONENTS
WHICH ORDER
WHICH DATA
WHICH ACTIONS
```

The application controls:

```
WHICH COMPONENTS EXIST
HOW COMPONENTS ARE RENDERED
WHICH ACTIONS ARE ALLOWED
DESIGN SYSTEM
SECURITY
```

### Forbidden architecture

**NEVER** implement this architecture:

```
User → LLM → Generated React code → Browser
```

That is NOT the goal.

The architecture **MUST** be:

```
User
  ↓
Agent
  ↓
Structured A2UI
  ↓
Validated Catalog
  ↓
Existing Renderer
  ↓
Native React Components
```

Do **NOT**:

- create separate applications
- create separate React applications
- hard-code `WeatherPage`, `NewsPage`, `TravelPage`, `MarketPage`
- let the LLM return JSX, HTML, or JavaScript
- execute arbitrary code from the LLM
- invent components that are not in `AppCatalog`

Required pipeline:

```
User Intent
    ↓
Intent Router
    ↓
Domain Agent
    ↓
A2UI Plan
    ↓
A2UI Renderer
    ↓
Component Catalog
    ↓
Dynamic UI
```

---

## 3. Technology stack

Use this stack. Do not substitute unless the developer explicitly asks.

### Frontend

- React
- Vite
- TypeScript (not JavaScript)
- Tailwind CSS
- Lucide React
- Zustand
- JSON Pointer (RFC 6901)

### Backend

- Python 3.11+
- FastAPI
- asyncio
- SSE (`sse-starlette` or equivalent)
- [`a2ui-agent-sdk`](https://pypi.org/project/a2ui-agent-sdk/) — required for catalog loading, `A2uiSchemaManager` system prompts, parse/heal/validate
- Optional: `google-adk` when the selected LLM provider is Google Gemini and ADK `LlmAgent` is a convenient host. **Do not require ADK** for OpenAI, Anthropic, Ollama, or OpenAI-compatible providers. Those hosts use the same A2UI prompt + validation loop through `LLMProvider`.

### Protocol

- A2UI v1.0 candidate message semantics (`createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`, `actionResponse`), with a custom catalog named `AppCatalog`
- Agent generation follows [A2UI Agent Development](https://a2ui.org/guides/agent-development/) and the Python [agent SDK guide](https://github.com/a2ui-project/a2ui/blob/main/agent_sdks/python/a2ui_agent/agent_development.md)
- Prefer `VERSION_0_9` / v1.0 in `A2uiSchemaManager`. If the installed SDK only exposes `VERSION_0_8`, still emit this PoC's v1.0 envelope on the wire (`createSurface` / `updateComponents` / `updateDataModel`) and map internally.

Canonical references:

- https://a2ui.org/
- https://a2ui.org/specification/v1.0-a2ui/
- https://a2ui.org/guides/agent-development/
- https://a2ui.org/guides/defining-your-own-catalog/

This PoC uses A2UI semantics over SSE + REST. It does not need a full A2A/AG-UI transport stack, but **message generation, catalog prompting, and validation must follow the official agent-development pattern**.

### Tests

- Frontend: Vitest + React Testing Library
- Backend: pytest + httpx `AsyncClient`
- At least one Playwright (or equivalent) end-to-end demo test

### Tooling

- `pnpm` or `npm` for the frontend (prefer `pnpm` if available)
- `uv` or `pip` for the backend (prefer `uv` if available)
- Docker Compose when the developer selected Docker or Both

---

## 4. Repository layout

Generate this structure (names may vary slightly, responsibilities must not):

```
.
├── skills.md                          # this specification (already exists; do not overwrite)
├── README.md
├── .env.example
├── .env.local                         # gitignored; created from .env.example
├── .gitignore
├── docker-compose.yml                 # if Docker or Both
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── a2ui/
│       │   ├── types.ts
│       │   ├── validate.ts
│       │   ├── jsonPointer.ts
│       │   ├── sseClient.ts
│       │   ├── actions.ts
│       │   └── A2UIRenderer.tsx
│       ├── catalog/
│       │   ├── AppCatalog.ts
│       │   ├── schemas.ts
│       │   └── components/            # one file per catalog component
│       ├── store/
│       │   ├── a2uiStore.ts
│       │   └── demoStore.ts
│       ├── demo/
│       │   ├── DemoShell.tsx
│       │   ├── IntentInput.tsx
│       │   ├── UserContextPanel.tsx
│       │   ├── AgentActivityPanel.tsx
│       │   ├── NetworkInspector.tsx
│       │   ├── ArchitectureView.tsx
│       │   ├── DevicePreview.tsx
│       │   └── PipelineAnimation.tsx
│       └── lib/
│           └── env.ts                 # public Vite env only; never LLM keys
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── sse.py
│   │   ├── errors.py
│   │   ├── llm/
│   │   │   ├── base.py
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   ├── openai_compatible.py
│   │   │   └── factory.py
│   │   ├── agents/
│   │   │   ├── base_a2ui_agent.py      # shared: tools → A2UI generate → validate → messages
│   │   │   ├── prompt_builder.py       # A2uiSchemaManager.generate_system_prompt per domain
│   │   │   ├── intent_router.py
│   │   │   ├── orchestrator.py
│   │   │   ├── activity.py
│   │   │   ├── weather_agent.py        # only if WEATHER enabled
│   │   │   ├── news_agent.py           # only if NEWS enabled
│   │   │   ├── travel_agent.py
│   │   │   ├── market_agent.py
│   │   │   ├── shopping_agent.py
│   │   │   ├── fintech_agent.py
│   │   │   └── customer_support_agent.py
│   │   ├── providers/
│   │   │   ├── weather.py
│   │   │   ├── news.py
│   │   │   ├── market.py
│   │   │   ├── flights.py
│   │   │   ├── hotels.py
│   │   │   ├── shopping.py
│   │   │   ├── fintech.py
│   │   │   └── support.py
│   │   ├── a2ui/
│   │   │   ├── messages.py
│   │   │   ├── catalog.py
│   │   │   ├── schema_manager.py       # wraps A2uiSchemaManager + AppCatalog
│   │   │   ├── validate.py
│   │   │   ├── parse.py                # parse_response / DirectJsonStreamParser
│   │   │   ├── catalogs/
│   │   │   │   └── AppCatalog.json     # freestanding custom catalog schema
│   │   │   └── examples/               # few-shot A2UI JSON per enabled domain
│   │   │       ├── weather/
│   │   │       ├── news/
│   │   │       ├── travel/
│   │   │       ├── market/
│   │   │       ├── shopping/
│   │   │       ├── fintech/
│   │   │       └── customer_support/
│   │   └── api/
│   │       ├── stream.py
│   │       └── actions.py
│   └── tests/
└── frontend/src/__tests__/  and/or frontend tests colocated
```

Do not put LLM keys, weather keys, news keys, or market keys in `frontend/`.

---

## 5. API key configuration

Never hard-code API keys.

Create `.env.example`:

```
LLM_PROVIDER=
LLM_MODEL=
LLM_API_KEY=
LLM_BASE_URL=

WEATHER_API_KEY=
NEWS_API_KEY=
MARKET_API_KEY=

DATA_MODE=mock
ENABLED_DOMAINS=WEATHER,NEWS,TRAVEL,MARKET_DATA,SHOPPING,FINTECH,CUSTOMER_SUPPORT

CORS_ORIGINS=http://localhost:5173
```

Create `.env.local` for local development by copying `.env.example`.

The generated application must read secrets **only** from environment variables.

The README must explain:

1. Copy `.env.example` to `.env.local`
2. Add API keys
3. Start the application

Example:

```bash
cp .env.example .env.local
```

Then configure:

```
LLM_PROVIDER=openai
LLM_MODEL=<selected-model>
LLM_API_KEY=<your-key>
```

### Critical security rule

**Never expose LLM API keys to the browser.**

LLM communication must happen through the backend.

Frontend may know only:

- `VITE_API_BASE_URL` (e.g. `http://localhost:8000`)
- demo flags that are not secrets

Backend loads `.env.local` via pydantic-settings / python-dotenv.

`.gitignore` must include:

```
.env.local
.env
*.pem
```

`.env.example` must be committed. `.env.local` must not.

---

## 6. Architecture

```
USER
  ↓
INTENT ROUTER
  ↓
DOMAIN AGENTS
  ↓
TOOLS / APIS
  ↓
A2UI GENERATOR
  ↓
SSE
  ↓
A2UI RUNTIME
  ↓
COMPONENT CATALOG
  ↓
REACT
```

### Frontend responsibilities

- Demo shell (left inspector + right canvas)
- Natural-language input
- User context (role, device, locale, preferences)
- SSE client
- A2UI message validation
- Zustand surface store
- JSON Pointer resolver
- Catalog-backed renderer
- Local `functionCall` execution
- Remote `event` posting
- Network inspector
- Agent activity panel
- Desktop / mobile / multi-user preview

### Backend responsibilities

- Config and secrets
- LLM provider factory
- Intent Router Agent
- Domain A2UI agents for **each enabled experience**, built with `a2ui-agent-sdk` (`A2uiSchemaManager`, catalog examples, parse/validate)
- External API adapters (real or mock) exposed as agent **tools**
- A2UI message validation before streaming (never send unvalidated LLM JSON)
- SSE stream at `GET /api/stream`
- Remote actions at `POST /api/handle-action`
- Agent activity events on the same stream
- Fallback Mock Agent Mode

### Data flow for a user query

1. User submits natural language + current user context.
2. Frontend opens `GET /api/stream` (or POSTs intent then subscribes; see SSE section).
3. Backend Intent Router classifies `{ domain, intent, entities }` (no UI).
4. Matching **enabled** Domain A2UI Agent calls tools/adapters, then generates A2UI JSON using `A2uiSchemaManager` + `AppCatalog` (or hydrates the same examples in Mock Agent Mode).
5. Backend parses, heals, and validates messages, then streams `createSurface` → `updateComponents` → `updateDataModel`.
6. Frontend validates each message, updates the store, and renders incrementally.
7. User interactions either run local `functionCall`s or POST remote `event`s.
8. Remote actions may return `actionResponse` and further `updateDataModel` / `updateComponents`.

---

## 7. A2UI protocol requirements

Implement A2UI v1.0 message semantics.

Every agent-to-renderer message is a JSON object with:

- `"version": "v1.0"`
- exactly one of these keys: `createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`, `actionResponse`

This PoC also streams non-A2UI demo envelopes on the same SSE connection for the inspector/activity panels. Those MUST use a distinct key so they cannot be mistaken for A2UI:

```json
{ "version": "demo", "agentActivity": { "step": "intent_detected", "detail": "TRAVEL" } }
{ "version": "demo", "pipeline": { "stage": "INTENT_ROUTER" } }
```

The renderer must ignore unknown `version: "demo"` messages for UI rendering, but the Network Inspector must display them.

### 7.1 createSurface

Signals the renderer to create a new surface.

```json
{
  "version": "v1.0",
  "createSurface": {
    "surfaceId": "weather_surface",
    "catalogId": "AppCatalog",
    "sendDataModel": false
  }
}
```

Rules:

- `surfaceId` is globally unique for the renderer lifetime.
- Creating an existing `surfaceId` without deleting it first is an error.
- `catalogId` for this PoC is always `"AppCatalog"`.
- The canonical Surface container always mounts the component with `"id": "root"`.
- Optional inline `components` and `dataModel` are allowed (v1.0 single-message instantiation), but the demo should usually stream them separately so the Network Inspector shows the lifecycle.

### 7.2 updateComponents

Provides a **flat adjacency-list** of components.

```json
{
  "version": "v1.0",
  "updateComponents": {
    "surfaceId": "weather_surface",
    "components": [
      {
        "id": "root",
        "component": "Page",
        "children": ["weather_root"]
      },
      {
        "id": "weather_root",
        "component": "Card",
        "children": ["temperature", "humidity", "rain"]
      },
      {
        "id": "temperature",
        "component": "MetricCard",
        "title": "Temperature",
        "value": { "path": "/weather/currentTemperature" }
      }
    ]
  }
}
```

Rules:

- Children reference component IDs. **No deeply nested component JSON.**
- Do not send a `parent` field. Parentage is implied by `children` / `child`.
- Use `"component"` as the discriminator (A2UI v1.0), not `"type"`.
- One component in the list MUST have `"id": "root"`.
- Missing child IDs must render placeholders, not crash (progressive rendering).
- Unknown `component` names must be rejected (see catalog).

### 7.3 updateDataModel

UI structure and dynamic data remain separate.

```json
{
  "version": "v1.0",
  "updateDataModel": {
    "surfaceId": "weather_surface",
    "path": "/weather",
    "value": {
      "currentTemperature": 31,
      "humidity": 62,
      "rainProbability": 20
    }
  }
}
```

Rules:

- `path` is a JSON Pointer. Default `/` replaces the entire model.
- `value` is required. Set `value` to `null` to delete the key at `path`.
- Components bind via `{ "path": "/weather/currentTemperature" }`.
- The renderer resolves paths reactively. Changing data must update the UI without recreating the component tree.

### 7.4 deleteSurface

```json
{
  "version": "v1.0",
  "deleteSurface": {
    "surfaceId": "weather_surface"
  }
}
```

Removes the surface, its components, and its data model.

When the user starts a new intent that maps to a different domain, delete the previous experience surface (or replace it) so the canvas transforms without reload.

### 7.5 Component object

Each component:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique within the surface |
| `component` | yes | Catalog type name |
| `catalogId` | no | Defaults to surface `catalogId` (`AppCatalog`) |
| `child` | no | Single child ID |
| `children` | no | List of child IDs, or a template `{ "componentId", "path" }` |
| `action` | no | `functionCall` or `event` |
| other props | per schema | Literals or `{ "path": "..." }` bindings |
| `accessibility` | no | `label`, `description`, `live`, `hidden` |

### 7.6 Adjacency-list example from this spec

The following is the required mental model (flat list, children are IDs):

```json
[
  {
    "id": "weather_root",
    "component": "Card",
    "children": ["temperature", "humidity", "rain"]
  }
]
```

Never nest full component objects inside `children`.

---

## 8. Surface management

Zustand store shape:

```ts
surfaces[surfaceId] = {
  catalog: "AppCatalog",
  components: Map<string, A2UIComponent> | Record<string, A2UIComponent>,
  dataModel: object,
  status: "creating" | "ready" | "error" | "deleted"
}
```

Example:

```json
{
  "weather_surface": {
    "catalog": "AppCatalog",
    "components": [],
    "dataModel": {}
  }
}
```

Store operations:

- `createSurface(surfaceId, catalogId)`
- `updateComponents(surfaceId, components[])` — upsert by `id`
- `updateDataModel(surfaceId, path, value)` — JSON Pointer set/delete
- `deleteSurface(surfaceId)`
- `activeSurfaceId` — the canvas renders this surface

Experience switching:

1. Stream `deleteSurface` for the previous experience (if any).
2. Stream `createSurface` for the new domain.
3. Stream `updateComponents` then `updateDataModel`.

The React app must **not** remount the Vite application or navigate to a different route to change domains. Query/hash may update for deep links, but the renderer stays mounted.

---

## 9. Data model isolation and JSON Pointer

UI structure ≠ data.

Component:

```json
{
  "id": "temperature",
  "component": "MetricCard",
  "value": { "path": "/weather/currentTemperature" }
}
```

Data model:

```json
{
  "weather": {
    "currentTemperature": 31
  }
}
```

Supported example paths:

- `/weather/currentTemperature`
- `/weather/rainProbability`
- `/news/articles/0/title`
- `/travel/flight/price`
- `/market/nifty/value`

Implement RFC 6901:

- `~1` → `/`
- `~0` → `~`
- numeric segments index arrays
- missing paths return `undefined` and the component shows a bound-value placeholder or empty state
- invalid pointers (not starting with `/`, malformed `~` escapes) raise a developer-friendly error in the canvas and inspector:

```
Invalid JSON Pointer: <pointer>
```

Two-way bindings (inputs, tabs, filters):

- Local edits write back into the surface data model.
- Do not round-trip to the server unless the action is a remote `event`.

---

## 10. Component catalog — AppCatalog

Create **one global catalog**: `AppCatalog`.

The catalog is shared by ALL business experiences.

The catalog must be explicit. The agent cannot invent components.

If the agent sends `"SuperFancyWidget"`, the renderer must reject it and display:

```
Unsupported A2UI component:
SuperFancyWidget
```

### 10.1 Required catalog components

Implement and register all of the following:

| Name | Role |
| --- | --- |
| `Page` | Root layout wrapper |
| `Card` | Generic container |
| `MetricCard` | Label + value + optional delta |
| `List` | Collection container |
| `ListItem` | Row inside a list |
| `Table` | Tabular layout |
| `TableRow` | Row inside a table |
| `Badge` | Small label |
| `StatusChip` | Status with semantic color |
| `Button` | Clickable action |
| `Image` | Image with alt text |
| `Chart` | Line/bar/area chart (use a lightweight chart lib or SVG) |
| `Tabs` | Tab bar + panels |
| `Progress` | Progress bar |
| `Timeline` | Ordered events |
| `Alert` | Info/warn/error banner |
| `WeatherCard` | Domain weather summary |
| `NewsCard` | Article teaser |
| `TravelCard` | Trip summary |
| `MarketCard` | Instrument / index summary |
| `ProductCard` | Product teaser |
| `InvoiceTable` | Invoice list table |
| `MilestoneCard` | Freelancer milestone |

Also register these **demo aliases** so example UIs can be composed without inventing types. Each alias MUST map to a real React component or a thin wrapper around an existing one:

| Name | Implementation note |
| --- | --- |
| `ForecastChart` | Wrapper around `Chart` |
| `NewsList` | Wrapper around `List` |
| `FlightCard` | Wrapper around `TravelCard` or dedicated card |
| `HotelCard` | Wrapper around `TravelCard` or dedicated card |
| `ProductList` | Wrapper around `List` |
| `Rating` | Star rating display |
| `Price` | Currency display |
| `CompareButton` | Wrapper around `Button` |
| `PayButton` | Wrapper around `Button` |
| `OrderCard` | Order summary card |
| `RefundButton` | Wrapper around `Button` |

If an alias is a wrapper, it still must be a registered catalog key. Unregistered names are always rejected.

### 10.2 Catalog registration contract

`AppCatalog` is a TypeScript map:

```ts
{
  [componentName: string]: {
    component: React.FC<A2UIComponentProps>
    schema: JSONSchema
    allowedActions: Array<"functionCall" | "event">
    allowedEventNames?: string[]
    allowedFunctionNames?: string[]
  }
}
```

Backend keeps a parallel allowlist of component names and action names. The A2UI planner must only emit registered names. The frontend validator is the last line of defense.

### 10.3 Adding a new component

Document this process in README and follow it in code:

1. Create the React component under `frontend/src/catalog/components/`.
2. Add catalog registration in `AppCatalog.ts`.
3. Define the A2UI JSON schema (props, bindings, children).
4. Define data bindings (`path` fields).
5. Define allowed actions.
6. Add tests.
7. Add a demo snippet or mock surface that uses it.

The agent cannot use the component until it is registered.

---

## 11. Frontend architecture

### 11.1 A2UIRenderer

`A2UIRenderer` takes `surfaceId`, reads components + dataModel from the store, and recursively renders from `id: "root"`.

Pseudocode:

```
function renderNode(id):
  component = components[id]
  if !component: return <Placeholder missing={id} />
  entry = AppCatalog[component.component]
  if !entry: return <CatalogError name={component.component} />
  props = resolveBindings(component, dataModel)
  children = resolveChildren(component)
  return <entry.component {...props}>{children}</entry.component>
```

Never use `eval`, `new Function`, `innerHTML` with agent strings, or `dangerouslySetInnerHTML` for agent content. Text is always escaped by React. Images only load `https:` URLs (or local placeholders). Markdown is optional and must be sanitized if used; default is plain text.

### 11.2 Design system

Use Tailwind. Keep a coherent visual language across all domains:

- Neutral canvas background
- White/elevated cards
- Lucide icons
- Status colors: success / warning / danger / info
- Typography: clear hierarchy, not a marketing landing page
- Indian locale defaults for currency (`INR`, `en-IN`) and example cities (Hyderabad, Goa)

The design system belongs to the application, not the agent. Agent messages may request `variant` values defined in schemas (`primary`, `danger`, `compact`) but must not send raw CSS or className strings.

### 11.3 Demo shell UX

Polished Demo Mode layout:

**LEFT column**

- User input ("What do you want to do?")
- User context (role, device, locale, preferences)
- Domain detected
- Agent activity
- Network inspector

**RIGHT column**

- Dynamic A2UI canvas
- Desktop / Mobile preview toggle
- Optional Architecture view

When the user submits, animate the pipeline:

```
User Intent
    ↓
Intent Router
    ↓
Domain Agent
    ↓
A2UI
    ↓
Renderer
    ↓
UI
```

Highlight the current stage as SSE activity events arrive.

Banner at the top when Mock Agent Mode is active:

```
DEMO MODE
```

Do not pretend a real LLM is being used.

If a real LLM is configured, show a small "Live LLM: {provider}/{model}" chip instead.

### 11.4 Mobile demonstration

Provide:

- Desktop preview
- Mobile preview (width ~390px framed device chrome)

Also support **Multi-user preview** with the same codebase, renderer, and catalog:

| User | Role |
| --- | --- |
| User A | SME Owner |
| User B | Freelancer |
| User C | Finance Manager |

Switching users changes `userContext` sent with the next query. Domain agents / planner may compose different A2UI (for example: SME Owner sees business invoices + payout; Freelancer sees milestone release; Finance Manager sees risk/aging metrics). Do not swap React trees by role. Only the A2UI composition changes.

### 11.5 Agent activity panel

Show orchestration, for example:

```
✓ Intent detected: TRAVEL
✓ Travel Agent started
✓ Weather Agent consulted
✓ Flight data retrieved
✓ Hotel data retrieved
✓ A2UI surface created
✓ 8 components rendered
```

This must be driven by `agentActivity` demo events from the backend, not hardcoded after the fact.

### 11.6 Network inspector

Show raw A2UI (and demo) messages:

- `createSurface`
- `updateComponents`
- `updateDataModel`
- `deleteSurface`
- `event`
- `actionResponse`

Each row:

- timestamp
- surface ID
- message type
- expandable JSON payload

This demonstrates that the UI is actually protocol-driven.

### 11.7 Architecture view

Optional visual diagram (SVG or HTML/CSS, not a screenshot):

```
USER
  ↓
INTENT ROUTER
  ↓
DOMAIN AGENTS
  ↓
TOOLS / APIS
  ↓
A2UI GENERATOR
  ↓
SSE
  ↓
A2UI RUNTIME
  ↓
COMPONENT CATALOG
  ↓
REACT
```

Highlight the active node during a live request.

---

## 12. Backend architecture

FastAPI app with CORS restricted to the Vite origin.

### HTTP API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness; reports `llmConfigured`, `dataMode`, `enabledDomains` |
| `GET` | `/api/stream` | SSE: intent → agents → A2UI + activity |
| `POST` | `/api/handle-action` | Remote events |
| `GET` | `/api/catalog` | Returns AppCatalog names (no secrets) |

Do not expose provider API keys, raw prompts with secrets, or `.env` contents.

### Request to `/api/stream`

Prefer:

```
GET /api/stream?q=<url-encoded prompt>
```

with JSON body not available on GET, so also accept:

```
POST /api/stream
Content-Type: application/json
```

Body:

```json
{
  "text": "What's the weather in Hyderabad tomorrow?",
  "userContext": {
    "user": { "id": "demo-user", "role": "business-owner" },
    "device": { "type": "mobile" },
    "preferences": { "compact": true },
    "locale": "en-IN",
    "currentIntent": "What's the weather in Hyderabad tomorrow?"
  },
  "activeSurfaceId": null
}
```

If the hosting stack makes POST SSE awkward, use:

1. `POST /api/sessions` → `{ sessionId }`
2. `GET /api/stream?sessionId=`

Either is acceptable. Document the chosen shape in README. The canvas must start rendering as messages arrive.

### SSE format

`Content-Type: text/event-stream`

Each event is one JSON envelope:

```
event: a2ui
data: {"version":"v1.0","createSurface":{...}}

event: a2ui
data: {"version":"v1.0","updateComponents":{...}}

event: a2ui
data: {"version":"v1.0","updateDataModel":{...}}

event: demo
data: {"version":"demo","agentActivity":{...}}
```

Flush after every message. **Do not wait for the complete response before sending the first `createSurface`.**

On completion send `event: done`. On failure send an A2UI `Alert` surface or a demo error event, then `event: done`.

Reconnect: if the SSE disconnects mid-flight, the frontend shows:

```
SSE disconnected. Retrying…
```

and may retry once. Do not duplicate surfaces on retry; use a request id.

---

## 13. Intent Router

Create an Intent Router Agent.

It classifies the user's request. It must **NOT** generate React. It must only determine intent and context.

Output contract:

```json
{
  "domain": "WEATHER",
  "intent": "WEATHER_FORECAST",
  "entities": {
    "location": "Hyderabad"
  },
  "confidence": 0.92
}
```

### Examples

Input: `"What's the weather in Hyderabad?"`

```json
{
  "domain": "WEATHER",
  "intent": "WEATHER_FORECAST",
  "entities": { "location": "Hyderabad" }
}
```

Input: `"Plan a trip to Goa."`

```json
{
  "domain": "TRAVEL",
  "intent": "PLAN_TRIP",
  "entities": { "destination": "Goa" }
}
```

Input: `"How is the Indian market doing?"`

```json
{
  "domain": "MARKET_DATA",
  "intent": "MARKET_OVERVIEW",
  "entities": { "market": "INDIA" }
}
```

### Domains and intents

| Domain | Example intents |
| --- | --- |
| `WEATHER` | `WEATHER_FORECAST`, `WEATHER_CURRENT` |
| `NEWS` | `NEWS_HEADLINES`, `NEWS_TOPIC` |
| `TRAVEL` | `PLAN_TRIP`, `FIND_FLIGHTS`, `FIND_HOTELS` |
| `MARKET_DATA` | `MARKET_OVERVIEW`, `INSTRUMENT_QUOTE` |
| `SHOPPING` | `PRODUCT_SEARCH`, `PRODUCT_COMPARE` |
| `FINTECH` | `INVOICES_ATTENTION`, `RELEASE_MILESTONE`, `EXECUTE_PAYOUT` |
| `CUSTOMER_SUPPORT` | `ORDER_STATUS`, `REQUEST_REFUND` |

If the domain is disabled by setup answers, the router must not select it. Fall back to a helpful `Alert` surface: domain not enabled.

If confidence is low, emit a clarification surface using `Card` + `Button` options, still via A2UI.

In Mock Agent Mode, classify with deterministic keyword/entity rules (see Part 16). In Live LLM Mode, ask the LLM for structured JSON matching a pydantic schema. Validate the JSON. On parse failure, fall back to mock rules and label the activity panel accordingly.

---

## 14. Domain agents — official A2UI agent development

Every domain agent MUST be built using the official A2UI agent-development loop from [https://a2ui.org/guides/agent-development/](https://a2ui.org/guides/agent-development/):

1. **Understand user intent** → decide what UI to show
2. **Generate A2UI JSON** → LLM structured output / catalog-driven prompts
3. **Validate & stream** → check schema, send to the client
4. **Handle actions** → respond to user interactions

Do **not** implement domain agents as "fetch data then dump JSON into a hardcoded React page."

Do **not** implement domain agents as "LLM returns JSX/HTML."

The correct split:

| Layer | Owns | Must not do |
| --- | --- | --- |
| Domain **tools / providers** | Fetch and normalize business data | Emit UI, JSX, HTML, or DOM |
| Domain **A2UI agent** | Generate `createSurface` / `updateComponents` / `updateDataModel` from that data + `AppCatalog` | Invent unregistered components or executable code |
| Renderer | Map catalog names to native React | Trust unvalidated LLM output |

### 14.0 Only chosen experiences

Implement A2UI agents **only for the business experiences selected in Part 0**.

| Setup answer | Agents to generate |
| --- | --- |
| A Weather | `WeatherAgent` |
| B News | `NewsAgent` |
| C Travel | `TravelAgent` (may consult Weather tools if Weather is also enabled; otherwise use WeatherProvider mock) |
| D Market Data | `MarketAgent` |
| E Shopping | `ShoppingAgent` |
| F Fintech | `FintechAgent` |
| G Customer Support | `CustomerSupportAgent` |
| H All | all seven |

If a domain is not enabled:

- Do not register its agent with the orchestrator.
- Do not include its example chips on the home screen.
- If the Intent Router would have selected it, emit an A2UI `Alert` surface: domain not enabled.

The Intent Router, `AppCatalog`, renderer, store, and SSE path stay shared. New domains plug in; they do not fork the app.

### 14.1 Required Python SDK wiring

Install and use `a2ui-agent-sdk`.

Initialize **one** `A2uiSchemaManager` around the custom `AppCatalog` (see [Defining Your Own Catalog](https://a2ui.org/guides/defining-your-own-catalog/)). Do not prompt the LLM with only the A2UI Basic Catalog — this PoC's design system is `AppCatalog`.

```python
from a2ui.schema.constants import VERSION_0_9
from a2ui.schema.manager import A2uiSchemaManager, CatalogConfig
# Import paths may be `a2ui.strategies.schema` / `a2ui.core.schema.manager`
# depending on SDK version — detect at install time and document the chosen import.

app_catalog = CatalogConfig.from_path(
    name="AppCatalog",
    catalog_path="app/a2ui/catalogs/AppCatalog.json",
    examples_path="app/a2ui/examples",
)

schema_manager = A2uiSchemaManager(
    version=VERSION_0_9,
    catalogs=[app_catalog],
)
```

Rules:

- `AppCatalog.json` must be **freestanding** (no external catalog `$ref`s except A2UI common types).
- Catalog `catalogId` on the wire is `"AppCatalog"`.
- Few-shot examples live under `examples/<domain>/` as valid A2UI JSONL or JSON message lists.
- `validate_examples=True` when generating prompts so bad examples cannot ship.

### 14.2 Generate the system prompt per domain

Each enabled domain agent gets its own instruction from `generate_system_prompt`, the same pattern as the restaurant-finder sample in the [Agent Development Guide](https://a2ui.org/guides/agent-development/).

```python
instruction = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,       # domain-specific
    workflow_description=WORKFLOW,           # call tools, then emit A2UI
    ui_description=UI_DESCRIPTION,           # which AppCatalog components / templates
    include_schema=True,
    include_examples=True,
    validate_examples=True,
    allowed_components=domain_allowed_components,  # prune tokens; still a subset of AppCatalog
    allowed_messages=["CreateSurfaceMessage", "UpdateComponentsMessage", "UpdateDataModelMessage", "DeleteSurfaceMessage"],
)
```

Shared prompt rules for **every** domain agent:

- Final output MUST be A2UI UI JSON (a list of envelopes), never React, HTML, JSX, or JavaScript.
- Call domain tools first; populate `updateDataModel.value` from tool results.
- Use adjacency-list components (`children` are IDs). Include `id: "root"`.
- Bind dynamic values with JSON Pointers (`{"path": "/weather/currentTemperature"}`).
- Only use `AppCatalog` component names listed in `allowed_components`.
- Only attach allowlisted `event` / `functionCall` names.

If `generate_system_prompt` injects `<a2ui-json>` wrapping instructions, the SSE parser MUST strip those fences before validation (see the official warning that raw `json.loads` is fragile — prefer SDK `parse_response` / `DirectJsonStreamParser`).

Host the instruction on `LLMProvider` (all vendors) or, when the developer chose Gemini, optionally on an ADK `LlmAgent` / `LiteLlm` as shown in the guide. The transport out of the process is still FastAPI SSE, not a required A2A server.

### 14.3 Tool-first, then A2UI

Mirror the restaurant agent in the official guide: tools return **data**, the agent then generates A2UI.

```python
def get_weather(location: str, date: str) -> str:
    """Call this tool to get normalized weather data."""
    return json.dumps(weather_provider.forecast(location, date))
```

Each domain agent:

1. Has a pydantic **input contract** (entities from the Intent Router + userContext).
2. Exposes 1+ **tools** backed by provider adapters (mock or live).
3. Normalizes tool JSON to a stable data-model shape.
4. Asks the LLM (or mock template) to emit A2UI messages that bind to that shape.

Agents must never return JSX, HTML, or manipulate the DOM.

### 14.4 Parse, validate, then stream

Follow "Understanding the Output" in the [Agent Development Guide](https://a2ui.org/guides/agent-development/):

1. Parse LLM output with the SDK parser (heal trailing commas / markdown fences).
2. Validate every message against `AppCatalog` / A2UI schema. **Never** send malformed UI to the client.
3. Stream validated envelopes over SSE incrementally (`createSurface` → `updateComponents` → `updateDataModel`).
4. Prefer incremental parsing (`DirectJsonStreamParser`) when the LLM host supports token streaming so the canvas paints before the full JSON block completes.
5. If validation fails: emit a developer `Alert` surface describing the failure; do not forward the illegal payload.

Frontend validation remains the last line of defense.

### 14.5 WeatherAgent

**Implement only if WEATHER is enabled.**

Input:

```json
{ "location": "Hyderabad", "date": "tomorrow" }
```

Tool: `get_weather` → WeatherProvider.

Normalized data example:

```json
{
  "location": "Hyderabad",
  "date": "2026-08-14",
  "temperature": 31,
  "humidity": 62,
  "rainProbability": 20,
  "condition": "Partly cloudy",
  "hourly": []
}
```

`ui_description` MUST require: `WeatherCard`, `MetricCard`, `Chart`/`ForecastChart`, `Alert`.

Example prompt rule: if `rainProbability >= 50`, include an `Alert`; otherwise omit it.

### 14.6 NewsAgent

**Implement only if NEWS is enabled.**

Input: `{ "topic": "AI", "timeRange": "today" }`

Tool: `get_news`.

`ui_description` MUST require: `NewsCard`, `NewsList`, `Image`, `Badge`, `Tabs`.

### 14.7 TravelAgent

**Implement only if TRAVEL is enabled.**

Input: `{ "destination": "Goa", "duration": "weekend" }`

Tools: `get_flights`, `get_hotels`, and `get_weather` when weather data is available.

`ui_description` MUST require: `TravelCard`, `WeatherCard`, `FlightCard`, `HotelCard`, `MetricCard`, `Button` (`book_trip`).

This is the primary **multi-agent / multi-tool** demo: activity panel should show Travel Agent started, weather consulted, flights retrieved, hotels retrieved, A2UI surface created.

### 14.8 MarketAgent

**Implement only if MARKET_DATA is enabled.**

Input: `{ "market": "INDIA" }`

Tool: `get_market_overview`.

`ui_description` MUST require: `MetricCard`, `Chart`, `Table`, `StatusChip`.

### 14.9 ShoppingAgent

**Implement only if SHOPPING is enabled.**

Input: `{ "query": "headphones", "maxPrice": 10000, "currency": "INR" }`

Tool: `search_products`.

`ui_description` MUST require: `ProductCard`, `ProductList`, `Rating`, `Price`, `CompareButton`.

### 14.10 FintechAgent

**Implement only if FINTECH is enabled.**

Input: `{ "focus": "invoices_attention" }` or `{ "focus": "release_milestone" }`

Tools: `get_invoices`, `get_milestones`.

`ui_description` MUST require: `MetricCard`, `InvoiceTable`, `StatusChip`, `PayButton` / `MilestoneCard`.

User context changes composition of the **same catalog**: Finance Manager vs Freelancer vs SME Owner.

### 14.11 CustomerSupportAgent

**Implement only if CUSTOMER_SUPPORT is enabled.**

Input: `{ "issue": "delayed_order", "desiredAction": "refund" }`

Tool: `get_order`.

`ui_description` MUST require: `OrderCard`, `StatusChip`, `Timeline`, `Alert`, `RefundButton`.

### 14.12 Orchestration

`Orchestrator` (this PoC's analog of the ADK root agent / restaurant guide flow):

1. Run Intent Router (structured JSON only — **the router does not generate A2UI**).
2. Dispatch the matching **enabled** domain A2UI agent.
3. Allow documented cross-domain tool consultation (Travel → Weather).
4. Emit `agentActivity` demo events at each step.
5. The domain agent generates A2UI (live LLM + `A2uiSchemaManager`, or mock examples).
6. Validate, then SSE stream.

Do not add a separate "planner that invents React." A leftover `a2ui_planner.py` is allowed **only** as the Mock Agent Mode template loader (it reads the same `examples/<domain>/` files the live prompt uses). Live mode must generate A2UI from the LLM using the official prompt/schema path.

---

## 15. A2UI generation (catalog + examples)

Live path:

```
tool result (structured data)
    ↓
domain agent + A2uiSchemaManager prompt
    ↓
A2UI JSON list
    ↓
parse / heal / validate against AppCatalog
    ↓
SSE: createSurface → updateComponents → updateDataModel
```

Mock path (no `LLM_API_KEY`):

```
tool result (structured data)
    ↓
select examples/<domain>/<intent>.json
    ↓
hydrate JSON Pointer data model with tool result
    ↓
validate against AppCatalog
    ↓
same SSE lifecycle
```

Example hydration: agent/tool data

```json
{
  "temperature": 31,
  "humidity": 62,
  "rainProbability": 20
}
```

becomes `updateDataModel` at `/weather`, while `updateComponents` stays the catalog example (WeatherCard / MetricCard / Chart / Alert).

Planner / generator rules (live and mock):

- Only `AppCatalog` component names.
- Flat adjacency lists.
- Bind values with JSON Pointers rather than inlining large text copies when data will update.
- Include an `id: "root"` `Page`.
- Attach remote `event` names only from the allowlist.
- Attach local `functionCall` names only from the catalog function allowlist.
- Prefer replacing the previous experience surface when domain changes.
- If the LLM emits an illegal component, replace it with `Alert` describing the validation failure — do not forward it to the browser.

Ship at least one validated few-shot example per enabled domain under `backend/app/a2ui/examples/`. Those files are both the live prompt examples and the mock surfaces. Keep them in sync with the demo UX in Part 21.

---

## 16. Fallback / Mock Agent Mode

If `LLM_API_KEY` is missing, the application must still run.

Offer **Mock Agent Mode**.

In Mock Agent Mode:

- Predefined intent detection (keywords + light NLP rules)
- The **same** `examples/<domain>/` A2UI files used as few-shot prompts for live agents, hydrated with tool/mock data
- Complete architecture still visible (router → domain A2UI agent → validate → SSE → renderer)
- No live LLM calls; still labeled DEMO MODE

Clearly label:

```
DEMO MODE
```

Do not pretend a real LLM is being used.

Mock routing hints:

| Keywords | Domain |
| --- | --- |
| weather, forecast, rain, temperature, Hyderabad, climate | WEATHER |
| news, headlines, AI news, article | NEWS |
| trip, travel, Goa, flight, hotel, weekend | TRAVEL |
| market, nifty, sensex, stock, Indian market | MARKET_DATA |
| headphones, buy, shopping, under ₹, product | SHOPPING |
| invoice, payout, milestone, freelancer, GST | FINTECH |
| refund, delayed, order, support, ticket | CUSTOMER_SUPPORT |

Mock data must look realistic for an Indian demo audience (INR, IST dates, NIFTY, Goa, Hyderabad).

---

## 17. LLM integration

Abstract the vendor.

```
LLMProvider
  ├── OpenAIProvider
  ├── AnthropicProvider
  ├── GeminiProvider
  ├── AzureOpenAIProvider   # can wrap OpenAI-compatible
  ├── OllamaProvider
  └── OpenAICompatibleProvider
```

Interface (Python):

```python
class LLMProvider(Protocol):
    async def complete_json(self, *, system: str, user: str, schema: dict | None = None) -> dict: ...
    async def complete_text_stream(self, *, system: str, user: str): ...
```

Factory reads `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`.

Rules:

- Agent logic must not import `openai` / `anthropic` directly outside the provider module.
- Setup questionnaire determines which provider is enabled.
- Timeouts: 20s default; then error + optional mock fallback for the demo.
- **System prompts for domain agents come from `A2uiSchemaManager.generate_system_prompt`**, not from ad-hoc "please return some JSON" strings.
- Prompts must instruct: return A2UI JSON only; never return HTML/JSX/JavaScript; only AppCatalog components.
- Prefer structured output / JSON mode when the vendor supports it; still validate with the catalog schema.
- When the provider is Gemini, `google-adk` `LlmAgent` + tools is an allowed host (as in the [Agent Development Guide](https://a2ui.org/guides/agent-development/)). Other providers use the same tools + prompt + validate loop on `LLMProvider`.

---

## 18. External API integration

Do not tightly couple business agents to external APIs. Use adapters.

```
WeatherProvider
NewsProvider
MarketProvider
FlightProvider
HotelProvider
ShoppingProvider
FintechProvider
SupportProvider
```

Each adapter has:

- `Mock*` implementation with fixture JSON
- `Live*` implementation behind the same protocol

`DATA_MODE=mock|real|mix` from env / setup answers.

In `mix`, use live adapters only when their API key exists; otherwise mock that domain and mark activity: `Using mock WeatherProvider (no WEATHER_API_KEY)`.

Live adapters must:

- keep keys server-side
- time out
- never send keys to the client
- normalize to the agent output contract

Suggested live APIs (swap freely if keys/docs differ; keep adapters swappable):

- Weather: Open-Meteo (no key) or OpenWeatherMap
- News: NewsAPI
- Market: a public market API or mock if unavailable
- Flights/Hotels: mock unless a key is provided
- Shopping/Fintech/Support: mock datasets are expected for the PoC

---

## 19. Action / event handling

Support two action types.

### LOCAL: `functionCall`

Examples: Search, Filter, Sort, Change tab.

These execute on the renderer. No network round-trip.

```json
{
  "action": {
    "functionCall": {
      "call": "changeTab",
      "args": { "tab": "hourly" }
    }
  }
}
```

Allowed local functions (catalog):

- `changeTab`
- `filterList`
- `sortList`
- `searchList`
- `toggleCompare`
- `setDevicePreview` (demo chrome only, if needed)

Unknown local functions show:

```
Unsupported local functionCall: <name>
```

Never execute a string of JavaScript.

### REMOTE: `event`

Examples:

- `execute_payout`
- `book_trip`
- `request_refund`
- `open_news`
- `refresh_market`
- `pay_invoice`
- `release_milestone`
- `search_products`

```json
{
  "action": {
    "event": {
      "name": "book_trip",
      "context": {
        "destination": { "path": "/travel/destination" }
      }
    }
  }
}
```

Frontend POSTs to `POST /api/handle-action`:

```json
{
  "name": "book_trip",
  "surfaceId": "travel_surface",
  "actionId": "uuid",
  "context": { "destination": "Goa" },
  "dataModel": { "...": "optional snapshot if sendDataModel" },
  "userContext": {}
}
```

Backend:

1. Validate `name` against the remote-action allowlist.
2. Reject unknown names with 400 and a developer message.
3. Execute the domain handler (mock or live).
4. Return JSON:

```json
{
  "actionResponse": {
    "actionId": "uuid",
    "value": { "status": "ok", "bookingId": "TR-1024" }
  },
  "messages": [
    { "version": "v1.0", "updateDataModel": { } }
  ]
}
```

The frontend applies `actionResponse` (inspector + optional UI) and any follow-up A2UI messages.

If `wantResponse` is used, correlate by `actionId`.

---

## 20. User context

Support:

```json
{
  "user": {
    "id": "demo-user",
    "role": "business-owner"
  },
  "device": {
    "type": "mobile"
  },
  "preferences": {
    "compact": true
  },
  "locale": "en-IN",
  "currentIntent": "Show my invoices"
}
```

Roles for multi-user preview:

- `business-owner` (SME Owner)
- `freelancer`
- `finance-manager`

The A2UI experience may change based on this context (density, which metrics, which CTAs). Same renderer, same catalog.

---

## 21. Dynamic experience examples

Implement mock (and live, if selected) surfaces that match these UX targets.

### WEATHER

User: `"What's the weather in Hyderabad tomorrow?"`

UI: `WeatherCard`, `MetricCard`, `ForecastChart`, `Alert`

### NEWS

User: `"Show me today's AI news."`

UI: `NewsCard`, `NewsList`, `Image`, `Badge`, `Tabs`

### TRAVEL

User: `"Plan a weekend trip to Goa."`

UI: `TravelCard`, `WeatherCard`, `FlightCard`, `HotelCard`, `MetricCard`, `Button`

### MARKET

User: `"How is the Indian market doing?"`

UI: `MetricCard`, `Chart`, `Table`, `StatusChip`

### SHOPPING

User: `"Find headphones under ₹10,000."`

UI: `ProductCard`, `ProductList`, `Rating`, `Price`, `CompareButton`

### FINTECH

User: `"Show me invoices that need attention."`

UI: `MetricCard`, `InvoiceTable`, `StatusChip`, `PayButton`

Also: `"I want to release my freelancer milestone."` → `MilestoneCard`

### CUSTOMER SUPPORT

User: `"My order is delayed. Can I get a refund?"`

UI: `OrderCard`, `StatusChip`, `Timeline`, `Alert`, `RefundButton`

### Transform without reload

Demonstrate:

```
WEATHER → NEWS → TRAVEL → MARKET → SHOPPING → FINTECH
```

in one session, submitting a new prompt each time. The canvas must swap surfaces via the A2UI lifecycle. This is a primary demo scenario.

---

## 22. UX requirements

- First screen: prominent `"What do you want to do?"` plus example chips that fill the input.
- Fast perceived performance: first `createSurface` should appear quickly; mock mode should feel instant.
- Progressive rendering as SSE messages arrive.
- Empty / loading / error states are themselves A2UI (`Alert`, `Progress`) when possible.
- Keyboard: Enter submits, Shift+Enter newline.
- Accessible labels on inputs, buttons, and catalog components.
- Canvas should feel like a product UI, not a JSON dump. JSON belongs in the inspector.

---

## 23. Security requirements

Never expose to the browser:

- LLM API keys
- third-party API keys
- secrets

All secrets stay server-side.

Additional rules:

- Validate all A2UI messages before rendering.
- Only allow components from `AppCatalog`.
- Validate remote actions against an allowlist.
- Never execute arbitrary JavaScript returned by the LLM.
- Never execute arbitrary HTML returned by the LLM.
- Never allow the LLM to generate executable frontend code.
- Strip `style`, `className`, `onclick`, `href="javascript:"` if they ever appear.
- Image URLs: allow `https:` and relative demo assets only.
- CORS allowlist.
- No `eval`, no dynamic `import()` of agent-supplied URLs.

---

## 24. Error handling

Handle all of the following with developer-friendly UI + inspector entries:

| Condition | Behavior |
| --- | --- |
| LLM unavailable | Activity error; optional mock fallback; `Alert` |
| API unavailable | Domain `Alert`; remaining UI still renders |
| Invalid A2UI | Reject message; show parse error; do not apply |
| Unsupported component | `Unsupported A2UI component: <name>` |
| Invalid JSON Pointer | `Invalid JSON Pointer: <path>` |
| Malformed message | Ignore for render; inspector shows error |
| SSE disconnect | Banner + single retry |
| Action failure | `actionResponse.error` + `Alert` |
| Timeout | `Alert` with timeout reason |
| Missing API key | DEMO MODE / mock adapters; never crash startup |
| Duplicate `surfaceId` | Error; do not overwrite silently |
| Action not allowlisted | 400 + canvas `Alert` |

Errors must be useful to a developer watching the demo, not generic "Something went wrong."

---

## 25. Testing requirements

Create tests for:

- Intent Router (keyword mock + schema validation)
- Domain A2UI agents (tool contract + example validation against AppCatalog)
- JSON Pointer resolver (get/set/delete, escapes, arrays)
- A2UI validation (happy path + malformed)
- Component catalog validation (unknown component rejected)
- Surface lifecycle (create/update/delete)
- Data model updates (reactive bind)
- SSE parsing
- Remote actions (allowlist + handler)
- Provider abstraction (factory selects mock vs live)
- Each enabled business experience (mock surface snapshot or agent output)
- At least one end-to-end demo test: submit "What's the weather in Hyderabad tomorrow?" and assert a `WeatherCard` (or catalog equivalent) appears

Frontend tests must not require real API keys.

---

## 26. Documentation

Generate `README.md` explaining:

1. What is A2UI?
2. Why this application exists
3. Architecture
4. How to configure an LLM
5. Where API keys go
6. How to run locally
7. Mock mode
8. Real API mode
9. Adding a new domain
10. Adding a new component
11. Adding a new agent (A2UI Agent Development Guide pattern)
12. A2UI lifecycle
13. Security
14. Demo scenarios

Include the setup copy:

```bash
cp .env.example .env.local
```

Local run (adjust if you choose Docker):

```bash
# backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# frontend
cd frontend && pnpm install && pnpm dev
```

Docker (if selected): `docker compose up --build`.

---

## 27. Adding a new business domain

The architecture must make adding a new domain easy.

Example: `SPORTS` should be addable by creating:

- `SportsAgent`
- `SportsProvider`

and composing **existing** components.

Do **not** require rewriting:

- `A2UIRenderer`
- `A2UIStore`
- `AppCatalog` (unless a genuinely new widget is needed)

Document the steps:

1. Add domain enum value.
2. Extend Intent Router labels/examples.
3. Implement provider adapter (mock first) as agent **tools**.
4. Implement the domain A2UI agent per [Agent Development](https://a2ui.org/guides/agent-development/): `generate_system_prompt`, tools, parse, validate.
5. Add `examples/<domain>/` few-shot A2UI JSON (also used in mock mode).
6. Register remote actions if any.
7. Add tests and a demo prompt chip.
8. Add to `ENABLED_DOMAINS`.

---

## 28. Adding a new agent

Follow the [A2UI Agent Development Guide](https://a2ui.org/guides/agent-development/) for every new domain:

1. Create `backend/app/agents/<name>_agent.py`.
2. Define input pydantic models and tool functions that return **data** (JSON), never UI.
3. Call providers, not raw HTTP, from those tools.
4. Add `examples/<domain>/*.json` few-shot A2UI messages; validate them with `A2uiSchemaManager`.
5. Build `ROLE_DESCRIPTION`, `WORKFLOW`, and `UI_DESCRIPTION`; call `generate_system_prompt` with `allowed_components` for that domain.
6. Parse / validate LLM output (or hydrate examples in mock mode) before SSE.
7. Register with the orchestrator **only if** the domain is in `ENABLED_DOMAINS`.
8. Add tests: tool contract, example validation, unsupported-component rejection.

Do not put React rendering code in the agent. The agent generates A2UI JSON only.

---

## 29. Implementation order

After the setup interview is answered, implement in this order:

1. Repo skeleton, `.gitignore`, `.env.example`, `.env.local`, README stub
2. Frontend Vite + React + TS + Tailwind + Zustand
3. `AppCatalog` with `Page`, `Card`, `Alert`, `MetricCard`, `Button` first
4. A2UI types, validator, JSON Pointer, store, renderer
5. Demo shell (input, canvas, inspector, activity)
6. FastAPI health + SSE that streams a **hardcoded** weather surface
7. Prove progressive rendering + inspector
8. Intent Router mock rules
9. `AppCatalog.json` + `A2uiSchemaManager` + few-shot examples **for each enabled domain only**
10. Domain A2UI agents (tools → generate A2UI → validate) for each enabled experience
11. Experience switching (`deleteSurface` / new surface)
12. Local `functionCall` + remote `event`
13. LLM provider abstraction + live `generate_system_prompt` path (if key present)
14. External adapters (mock + optional live)
15. User context / mobile / multi-user preview
16. Architecture view + pipeline animation
17. Tests (including catalog example validation and each enabled domain agent)
18. README completion
19. Docker if requested

Do not skip the hardcoded SSE weather slice. It de-risks the protocol before LLM work.

---

## 30. Demo requirements

A polished walkthrough must be possible in under two minutes:

1. Open the app. See "What do you want to do?" and DEMO MODE or Live LLM chip.
2. Click example: weather in Hyderabad. Left panel shows router → WeatherAgent → A2UI. Right panel renders weather UI. Inspector shows `createSurface` / `updateComponents` / `updateDataModel`.
3. Submit AI news. Canvas transforms without reload.
4. Submit Goa trip. Show multi-agent activity (Travel + Weather + flights/hotels).
5. Toggle mobile preview.
6. Switch to Freelancer vs Finance Manager and re-run invoices/milestone.
7. Trigger a remote action (`book_trip` or `request_refund`) and show `actionResponse`.
8. Optionally open Architecture view.

---

## 31. Acceptance criteria

The implementation generated from this file is complete only when:

- [ ] `skills.md` exists and is self-contained
- [ ] AI coding agent asks LLM provider before coding
- [ ] AI coding agent asks for model
- [ ] AI coding agent explains API key configuration
- [ ] API keys remain server-side
- [ ] `.env.example` exists
- [ ] Mock mode exists
- [ ] Real LLM mode exists
- [ ] Intent Router exists
- [ ] An A2UI-generating domain agent exists for **each chosen** business experience
- [ ] Domain agents follow https://a2ui.org/guides/agent-development/ (`A2uiSchemaManager`, tools, validate, stream)
- [ ] Disabled domains are not registered and show an A2UI `Alert` if requested
- [ ] A2UI runtime exists
- [ ] A2UI catalog exists (`AppCatalog.json` + React registry)
- [ ] A2UI validation exists (backend schema + frontend catalog)
- [ ] JSON Pointer bindings work
- [ ] Surface lifecycle works
- [ ] SSE works
- [ ] Local `functionCall` works
- [ ] Remote `event` works
- [ ] `actionResponse` works
- [ ] Weather experience works
- [ ] News experience works
- [ ] Travel experience works
- [ ] Market experience works
- [ ] Shopping experience works
- [ ] Fintech experience works
- [ ] Customer Support experience works
- [ ] User intent dynamically changes UI
- [ ] UI changes without application reload
- [ ] Mobile preview works
- [ ] Multi-user preview works
- [ ] Network Inspector works
- [ ] Agent Activity panel works
- [ ] Unsupported components are rejected
- [ ] No arbitrary code from LLM is executed
- [ ] README is generated
- [ ] Tests exist

---

## 32. What this skill must NOT do

- Do not overwrite this `skills.md` during implementation unless the developer asks.
- Do not start coding before the setup questionnaire is answered.
- Do not generate seven apps or seven routers/pages per domain.
- Do not put secrets in frontend bundles, README screenshots, or commit history.
- Do not implement `User → LLM → generated React`.

---

## 33. Quick reminder for the implementing agent

You are building **one** React + FastAPI application that speaks **A2UI**.

Agents generate validated A2UI JSON using `a2ui-agent-sdk` and `AppCatalog`, following [Agent Development](https://a2ui.org/guides/agent-development/). The catalog and renderer own how UI looks. Only implement domain agents the developer enabled in Part 0.

If `LLM_API_KEY` is absent, ship a labeled DEMO MODE that still proves the architecture.

Now: if you have not asked the setup questions in Part 0, ask them and wait. If you already have answers, implement according to this specification.
