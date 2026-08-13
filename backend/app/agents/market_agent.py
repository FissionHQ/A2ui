from app.agents.orchestrator import generate_a2ui, run_domain


class MarketAgent:
    name = "MarketAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("MARKET_DATA", entities, role)
        return data, await generate_a2ui("MARKET_DATA", data, role), notes
