from app.agents.orchestrator import generate_a2ui, run_domain


class CustomerSupportAgent:
    name = "CustomerSupportAgent"

    async def run(self, entities: dict, role: str = "business-owner"):
        data, notes = await run_domain("CUSTOMER_SUPPORT", entities, role)
        return data, await generate_a2ui("CUSTOMER_SUPPORT", data, role), notes
