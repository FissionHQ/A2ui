# A2UI Adaptive Experience Engine

One codebase. One renderer. One component catalog. Many business experiences.

This demo shows **Agent-to-UI (A2UI)**: agents emit validated declarative UI messages. The client renders them with a fixed React catalog. The LLM never generates React, HTML, or JavaScript.

Canonical protocol: [A2UI](https://a2ui.org/) · Agent loop: [Agent Development Guide](https://a2ui.org/guides/agent-development/)

```
USER → INTENT ROUTER → DOMAIN AGENTS → TOOLS/APIS → A2UI GENERATOR → SSE → RUNTIME → AppCatalog → REACT
```

The canvas becomes a weather, news, travel, market, shopping, fintech, or customer-support experience from natural language — without reloading the app.

## Setup recorded for this checkout

| Choice | Value |
| --- | --- |
| LLM provider | Google Gemini |
| Requested model | AntiGravity (`antigravity-preview-05-2026`) |
| Structured generation model | `gemini-3.6-flash` (Antigravity’s default underlying Gemini model) |
| API keys | `.env.local` (server-side only) |
| Experiences | All seven |
| Data | Mix: real **free** APIs when they work, otherwise mock |
| Run | Docker |

Antigravity is a [managed Gemini agent](https://ai.google.dev/gemini-api/docs/antigravity-agent) with a sandbox. This app needs **structured A2UI JSON**, so live mode calls Gemini `generateContent` with `GEMINI_GENERATION_MODEL` (default `gemini-3.6-flash`). The inspector still labels the run as Gemini / Antigravity.

If `LLM_API_KEY` is empty, the UI shows **DEMO MODE** and uses the same catalog examples the live agents are prompted with. It does not pretend a real LLM is in use.

## Configure an LLM (optional)

Never put keys in frontend code.

```bash
cp .env.example .env.local
```

Then edit `.env.local`:

```
LLM_PROVIDER=gemini
LLM_MODEL=antigravity-preview-05-2026
GEMINI_GENERATION_MODEL=gemini-3.6-flash
LLM_API_KEY=your-gemini-api-key
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

## Run with Docker (default)

```bash
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080).

API: [http://localhost:8000/api/health](http://localhost:8000/api/health).

## Mock mode vs real APIs

`DATA_MODE=mix` (this checkout):

| Domain | Live free API | Fallback |
| --- | --- | --- |
| Weather | [Open-Meteo](https://open-meteo.com/) geocoding + forecast | Mock Hyderabad forecast |
| News | [HN Algolia](https://hn.algolia.com/api) | Mock AI headlines |
| Market | Yahoo chart `^NSEI` | Mock NIFTY/SENSEX |
| Travel flights/hotels | — | Mock |
| Shopping / fintech / support | — | Mock datasets |

Set `DATA_MODE=mock` to skip the network.

## Architecture

- **Frontend:** React, Vite, TypeScript, [Fission UI](https://fissionhq.github.io/ui-design-system/) (branded shadcn), Zustand, Lucide. A2UI runtime validates messages, resolves JSON Pointers, and renders `AppCatalog` only. Catalog wrappers use Fission `Button`, `Card`, `Badge`, `Table`, `Tabs`, `Input`, `Select`, and `Dialog`.
- **Backend:** Python FastAPI, asyncio, SSE. Intent router, seven domain A2UI agents, provider adapters, catalog validation.
- **Security:** Secrets stay on the server. Unknown components are rejected (`Unsupported A2UI component: …`). Remote events are allowlisted. No `eval`, no `dangerouslySetInnerHTML`, no agent-supplied JavaScript.

### A2UI lifecycle

1. `createSurface` (`catalogId: AppCatalog`)
2. `updateComponents` (flat adjacency list, `id: "root"`)
3. `updateDataModel` (JSON Pointer paths)
4. `deleteSurface` when the experience changes
5. Local `functionCall` (tabs/compare) or remote `event` → `POST /api/handle-action` → `actionResponse`

## Adding a new domain

1. Add the enum to `ENABLED_DOMAINS` and the intent router.
2. Add a provider adapter (mock first) as tools.
3. Add `examples` via `app/a2ui/examples.py` and `generate_system_prompt` in `prompt_builder.py`.
4. Register the agent with the orchestrator.
5. Reuse `AppCatalog` components. Do not fork the renderer.

## Adding a new component

1. React component in `frontend/src/catalog/components.tsx`
2. Register in `AppCatalog.ts` and `backend/app/a2ui/catalog.py`
3. Schema + bindings + allowed actions
4. Tests + a demo surface

The agent cannot use it until it is registered.

## Adding a new agent

Follow [Agent Development](https://a2ui.org/guides/agent-development/): tools return data; `A2uiSchemaManager` / `prompt_for_domain` builds the system prompt; parse/validate before SSE.

## Demo scenarios

1. Open the app — see **What do you want to do?** and DEMO MODE (unless a Gemini key is set).
2. “What’s the weather in Hyderabad tomorrow?” — WeatherCard + metrics + chart.
3. “Show me today’s AI news.” — canvas transforms, no reload.
4. “Plan a weekend trip to Goa.” — Travel + weather + flight + hotel + Book.
5. Toggle mobile preview.
6. Switch Freelancer vs Finance Manager, then invoices / milestone.
7. Trigger **Book this trip** or **Request refund** and expand `actionResponse` in the inspector.
8. Architecture view (boxes icon).

## Tests

```bash
cd backend && pip install -e ".[dev]" && pytest
cd frontend && npm install && npm test
```

## Localhost without Docker

```bash
cd backend && pip install -e . && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

Frontend: http://localhost:5173 (Vite proxies `/api` to port 8000).
