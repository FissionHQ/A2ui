from app.a2ui.catalog import CATALOG_ID, COMPONENT_NAMES, DOMAIN_COMPONENTS, LOCAL_FUNCTIONS, REMOTE_EVENTS


def try_sdk_schema_manager():
    try:
        from a2ui.schema.constants import VERSION_0_9  # type: ignore
        from a2ui.schema.manager import A2uiSchemaManager, CatalogConfig  # type: ignore

        return VERSION_0_9, A2uiSchemaManager, CatalogConfig
    except Exception:
        try:
            from a2ui.strategies.schema import A2uiSchemaManager  # type: ignore
            from a2ui.schema.catalog import CatalogConfig  # type: ignore
            from a2ui.schema.constants import VERSION_0_9  # type: ignore

            return VERSION_0_9, A2uiSchemaManager, CatalogConfig
        except Exception:
            return None


class LocalSchemaManager:
    """Fallback A2uiSchemaManager compatible helper when a2ui-agent-sdk is absent."""

    version = "v1.0"

    def generate_system_prompt(
        self,
        *,
        role_description: str,
        workflow_description: str = "",
        ui_description: str = "",
        include_schema: bool = True,
        include_examples: bool = True,
        validate_examples: bool = True,
        allowed_components: list[str] | None = None,
        allowed_messages: list[str] | None = None,
    ) -> str:
        allowed = allowed_components or COMPONENT_NAMES
        messages = allowed_messages or [
            "createSurface",
            "updateComponents",
            "updateDataModel",
            "deleteSurface",
        ]
        schema_block = ""
        if include_schema:
            schema_block = f"""
A2UI v1.0 envelope: JSON object with "version": "v1.0" and exactly one of: {", ".join(messages)}.
catalogId must be "{CATALOG_ID}".
Components are a flat adjacency list. children are component id strings. One component must have id "root".
Discriminator field is "component" (not "type").
Bind dynamic values as {{"path": "/json/pointer"}}.
Allowed components: {", ".join(allowed)}.
Allowed local functionCall: {", ".join(sorted(LOCAL_FUNCTIONS))}.
Allowed remote event names: {", ".join(sorted(REMOTE_EVENTS))}.
Never return HTML, JSX, JavaScript, or React.
"""
        examples_note = ""
        if include_examples:
            examples_note = (
                "The few-shot example shows VALID A2UI shape only. "
                "Compose a NEW component tree that answers THIS userPrompt. "
                "Change which cards, metrics, alerts, and actions you include based on focus. "
                "Hydrate updateDataModel.value from tool results. Do not invent tool fields."
            )
        return f"""{role_description}

{workflow_description}

{ui_description}

{schema_block}

{examples_note}

Output a JSON array of A2UI messages only.
"""


def get_schema_manager():
    sdk = try_sdk_schema_manager()
    if sdk:
        _version, Manager, CatalogConfig = sdk
        try:
            from pathlib import Path

            catalog_path = Path(__file__).parent / "catalogs" / "AppCatalog.json"
            examples_path = Path(__file__).parent / "examples"
            cfg = CatalogConfig.from_path(
                name="AppCatalog",
                catalog_path=str(catalog_path),
                examples_path=str(examples_path),
            )
            return Manager(version=_version, catalogs=[cfg])
        except Exception:
            return LocalSchemaManager()
    return LocalSchemaManager()


def prompt_for_domain(domain: str) -> str:
    manager = get_schema_manager()
    allowed = DOMAIN_COMPONENTS.get(domain, COMPONENT_NAMES)
    roles = {
        "WEATHER": "You are a weather experience A2UI agent. Your final output MUST be A2UI UI JSON.",
        "NEWS": "You are a news experience A2UI agent. Your final output MUST be A2UI UI JSON.",
        "TRAVEL": "You are a travel planning A2UI agent. Your final output MUST be A2UI UI JSON.",
        "MARKET_DATA": "You are a market-data A2UI agent. Your final output MUST be A2UI UI JSON.",
        "SHOPPING": "You are a shopping A2UI agent. Your final output MUST be A2UI UI JSON.",
        "FINTECH": "You are a fintech invoicing/milestone A2UI agent. Your final output MUST be A2UI UI JSON.",
        "CUSTOMER_SUPPORT": "You are a customer-support A2UI agent. Your final output MUST be A2UI UI JSON.",
        "MOVIES": "You are a movies experience A2UI agent. Your final output MUST be A2UI UI JSON.",
        "BOOKS": "You are a books experience A2UI agent. Your final output MUST be A2UI UI JSON.",
    }
    ui = {
        "WEATHER": "Pick from WeatherCard, MetricCard, ForecastChart/Chart, Alert. If the user only asked about rain, lead with rain MetricCard + Alert. If they asked humidity or temperature, emphasize that metric. Still include WeatherCard for place/date.",
        "NEWS": "Pick from NewsCard, NewsList, Image, Badge, Tabs. Title the experience around the requested topic. Tabs can match topic facets.",
        "TRAVEL": "Pick from TravelCard, WeatherCard, FlightCard, HotelCard, MetricCard, Alert, Button (book_trip). Bind every matching hotel from toolResult.hotels; preserve airport distance, meal-plan, and price details. If focus is flights, you may omit hotels. If focus is hotels, emphasize all matched hotels. Never invent availability.",
        "MARKET_DATA": "Pick from MarketCard, MetricCard, Chart, Table, StatusChip, Alert, and NewsCard/NewsList. If focus is news_impact, lead with both index metrics, show the disclaimer, then bind news cards to toolResult.newsImpact.articles. Do not claim that correlation proves causation.",
        "SHOPPING": "Pick from ProductCard, ProductList, Rating, Price, CompareButton, CompareTray, Alert. Bind products to toolResult.products and compared to toolResult.compared. Heading must use toolResult.query. Never invent product titles.",
        "FINTECH": "Pick InvoiceTable + PayButton for invoices, MilestoneCard for milestones, MetricCard for totals. Respect user role.",
        "CUSTOMER_SUPPORT": "Pick OrderCard, StatusChip, Timeline, Alert, RefundButton. If they did not ask for a refund, you may omit RefundButton.",
        "MOVIES": "Pick ItemCard, ItemList, Tabs, Alert. Bind movies list to toolResult.movies. Use icon=film. Show director in director field. Never invent titles.",
        "BOOKS": "Pick ItemCard, ItemList, Alert. Bind books list to toolResult.books. Use icon=star. Show author in meta field. Never invent titles.",
    }
    workflow = (
        "1. Read userPrompt first. The UI must feel like an answer to that sentence.\n"
        "2. Use only tool JSON already provided. Do not invent APIs or extra facts.\n"
        "3. Emit createSurface, then updateComponents, then updateDataModel.\n"
        "4. Bind values with JSON Pointers. children are component ids, never nested objects.\n"
        "5. Never generate HTML, JSX, JavaScript, or React."
    )
    return manager.generate_system_prompt(
        role_description=roles.get(domain, "You are an A2UI agent."),
        workflow_description=workflow,
        ui_description=ui.get(domain, ""),
        include_schema=True,
        include_examples=True,
        validate_examples=True,
        allowed_components=allowed,
    )
