from app.agents.orchestrator import generate_a2ui, run_domain


class ShoppingAgent:
    name = "ShoppingAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("SHOPPING", entities, role)
        return data, await generate_a2ui("SHOPPING", data, role), notes
