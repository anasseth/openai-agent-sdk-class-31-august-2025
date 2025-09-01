import os
from dotenv import load_dotenv
from agents import Agent, RunConfig, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, enable_verbose_stdout_logging, function_tool, handoff, HandoffInputData
from agents.extensions import handoff_filters
load_dotenv()

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
# enable_verbose_stdout_logging()
# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
def simple_filter(data: HandoffInputData) -> HandoffInputData:
    print("\n\n[HANDOFF] Summarizing news transfer...\n\n")
    summarized_conversation = "Get latest tech news."
    
    print("\n\n[ITEM 1]", data.input_history)
    print("\n\n[ITEM 2]", data.pre_handoff_items)
    print("\n\n[ITEM 1]", data.new_items)
    
    return HandoffInputData(
        input_history=summarized_conversation,
        pre_handoff_items=(),
        new_items=(),
    )
@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."
# Agent 1 (news agent)
news_agent = Agent(
    name="NewsAgent",
    instructions="give the latest the news about user topic.",
    handoff_description="this agents is use for giving the news ",
    tools = [get_weather],
    model=llm_model,
)

# Agent 2 (main agent)
main_agent = Agent(
    name="MainAgent",
    instructions="you are the main agent first generate answer then handoffs to newsagent.",
    model=llm_model,
    tools = [get_weather],
    handoffs=[
        handoff(agent=news_agent, input_filter=simple_filter)],  # pyright: ignore[reportUndefinedVariable]
)

def main():
    res = Runner.run_sync(main_agent, "what is the weather in karachi and also what is the news of today", run_config= RunConfig(model = llm_model))
    print("\n👉 Final Response:", res.final_output)
    print("\n👉 Final agent:", res.last_agent.name)

if __name__ == "__main__":
    main()
