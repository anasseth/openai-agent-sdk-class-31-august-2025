import asyncio
from typing import Any
from agents import GuardrailFunctionOutput, HandoffInputData, InputGuardrailTripwireTriggered, OpenAIChatCompletionsModel, Agent, TResponseInputItem, handoff, input_guardrail, output_guardrail, function_tool, RunConfig, Runner, RunContextWrapper, set_tracing_disabled, enable_verbose_stdout_logging
from openai import AsyncOpenAI
from httpx import AsyncClient
# from pydantic import 
import logfire

enable_verbose_stdout_logging()
logfire.configure(token="")
logfire.instrument_openai_agents()

# GEMINI API KEY
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = "AIzaSyBvfElPEA0pW0cYnjaTzZO4hRMjI7tq6no"
GEMINI_BASE_URL = ""

# set_tracing_disabled(disabled=True)

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)
    
agent_a = Agent(name="Agent A", model=model)
agent_b = Agent(
    name="Agent B",
    instructions="Analyze user input and remove any sensitive data before handing offf to Agent A",
    handoffs=[agent_a],
    model=model
)
       
async def main():    
    async with AsyncClient() as client:
        logfire.instrument_httpx(client)
        result = await Runner.run(starting_agent=agent_b, input="i'm having chest pain. My bank account numbe is 568786798758697 and I have $2.5 Million Doolar", run_config=RunConfig(model=model), context=client)
    print(result.final_output)

def start():
    asyncio.run(main())
    
