from app.agents.orchestrator import generate_a2ui, run_domain


class NewsAgent:
    name = "NewsAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("NEWS", entities, role)
        return data, await generate_a2ui("NEWS", data, role), notes
