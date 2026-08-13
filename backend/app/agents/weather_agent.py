from app.agents.orchestrator import generate_a2ui, run_domain


class WeatherAgent:
    name = "WeatherAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("WEATHER", entities, role)
        messages = await generate_a2ui("WEATHER", data, role)
        return data, messages, notes
