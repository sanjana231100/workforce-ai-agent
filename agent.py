import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from tools import tools, web_search, sql_query, get_db_schema, calculator

load_dotenv()

# Tools without web search — used when web search mode is off
db_only_tools = [sql_query, get_db_schema, calculator]

# All tools including web search
all_tools = tools


def create_agent(web_search_enabled: bool = True):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    memory = MemorySaver()

    # Choose tool set based on web search toggle
    active_tools = all_tools if web_search_enabled else db_only_tools

    agent = create_react_agent(
        model=llm,
        tools=active_tools,
        checkpointer=memory,
    )

    return agent


def run_agent(agent, question: str, thread_id: str = "default") -> dict:
    """
    Invoke the agent with a question and return the response.
    thread_id groups messages into a conversation — same thread_id = shared memory.
    """
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    final_answer = result["messages"][-1].content

    # Extract tool call messages for CoT display
    intermediate_steps = [
        msg for msg in result["messages"]
        if not isinstance(msg, (HumanMessage, AIMessage))
    ]

    return {
        "output": final_answer,
        "intermediate_steps": intermediate_steps,
        "all_messages": result["messages"],
    }


if __name__ == "__main__":
    print("Initialising agent...")
    agent = create_agent()
    print("Agent ready. Type your question or 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            break
        if not question:
            continue

        print()
        result = run_agent(agent, question)

        for msg in result["intermediate_steps"]:
            print(f"[{msg.__class__.__name__}] {str(msg.content)[:200]}")

        print(f"\nFinal Answer: {result['output']}")
        print("-" * 60)