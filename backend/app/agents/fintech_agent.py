from app.agents.orchestrator import generate_a2ui, run_domain


class FintechAgent:
    name = "FintechAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("FINTECH", entities, role)
        return data, await generate_a2ui("FINTECH", data, role), notes
