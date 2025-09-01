import asyncio
from typing import Any
from agents import GuardrailFunctionOutput, HandoffInputData, InputGuardrailTripwireTriggered, OpenAIChatCompletionsModel, Agent, TResponseInputItem, handoff, input_guardrail, output_guardrail, function_tool, RunConfig, Runner, RunContextWrapper, set_tracing_disabled, enable_verbose_stdout_logging
from openai import AsyncOpenAI
from agents.run import AgentRunner, set_default_agent_runner

enable_verbose_stdout_logging()

# GEMINI API KEY
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = ""
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

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

class CustomRunner(AgentRunner):
    async def run(self, starting_agent: Any, user_input: Any, **kwargs: Any) -> Any:
        print("-------------------------")
        restricted_keywords = ["bank account", "account number", "credit card", "ssn", "social security", "password", "secret", "private key"]
        if any(keyword in str(user_input).lower() for keyword in restricted_keywords):
            print("Error: Input contains restricted information. Please remove sensitive data and try again.")
            return "Error: Input contains restricted information. Please remove sensitive data and try again."
        else:
            return await super().run(starting_agent, user_input, **kwargs)
    
set_default_agent_runner(CustomRunner())
       
async def main():
    result = await Runner.run(
        starting_agent=agent_b, 
        input="i'm having chest pain. My bank is 568786798758697 and I have $2.5 Million Dollar", 
        run_config=RunConfig(model=model)
        )
    print(result.final_output)
    print(result.last_agent.name)

def start():
    asyncio.run(main())
    
