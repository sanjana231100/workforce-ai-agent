import streamlit as st
import uuid
from agent import create_agent, run_agent

st.set_page_config(
    page_title="Workforce AI Agent",
    page_icon="🤖",
    layout="wide",
)

# ── Session state initialisation ──────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "latest_steps" not in st.session_state:
    st.session_state.latest_steps = []

if "web_search_enabled" not in st.session_state:
    st.session_state.web_search_enabled = True

if "agent" not in st.session_state:
    st.session_state.agent = create_agent(
        web_search_enabled=st.session_state.web_search_enabled
    )


# ── Functions ─────────────────────────────────────────────────────────────────

def render_cot_trace(steps: list):
    """Renders the chain-of-thought trace as collapsible expanders."""
    if not steps:
        return

    st.markdown("---")
    st.caption("🧠 Reasoning trace")

    for i, msg in enumerate(steps):
        class_name = msg.__class__.__name__
        content = str(msg.content) if msg.content else ""

        if class_name == "ToolMessage":
            tool_name = getattr(msg, "name", "tool")
            with st.expander(f"🔧 Tool call {i+1}: `{tool_name}`", expanded=False):
                st.code(content, language="text")

        elif class_name == "AIMessage" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                with st.expander(f"🤔 Thought → calling `{tc['name']}`", expanded=False):
                    st.code(str(tc.get("args", "")), language="python")


def process_question(question: str):
    """Runs the agent and renders the response with CoT trace."""
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(
                st.session_state.agent,
                question,
                thread_id=st.session_state.thread_id,
            )

        answer = result["output"]
        steps  = result["intermediate_steps"]

        st.write(answer)
        render_cot_trace(steps)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })
    st.session_state.latest_steps = steps


def reset_agent():
    """Recreates the agent with the current web search setting."""
    st.session_state.agent = create_agent(
        web_search_enabled=st.session_state.web_search_enabled
    )
    st.session_state.messages = []
    st.session_state.latest_steps = []
    st.session_state.thread_id = str(uuid.uuid4())


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 Workforce AI Agent")
    st.caption("Powered by LangGraph + Groq + SQLite")

    st.divider()

    # Web search toggle
    st.markdown("**Settings**")
    web_search_on = st.toggle(
        "Enable web search",
        value=st.session_state.web_search_enabled,
        help="When on, the agent can search the web for real-time information.",
    )

    # Recreate agent if the toggle changed
    if web_search_on != st.session_state.web_search_enabled:
        st.session_state.web_search_enabled = web_search_on
        reset_agent()
        st.rerun()

    # Show which tools are active
    if st.session_state.web_search_enabled:
        st.caption("🟢 SQL  🟢 Calculator  🟢 Web search")
    else:
        st.caption("🟢 SQL  🟢 Calculator  🔴 Web search")

    st.divider()

    # Example questions
    st.markdown("**Example questions**")
    example_questions = [
        "How many contractors in Engineering earn above $80k?",
        "What is the average salary by department?",
        "List the top 5 highest paid employees",
        "How many employees were hired in the last 2 years?",
        "Which department has the most Outstanding performers?",
        "What percentage of staff are contractors?",
    ]

    if st.session_state.web_search_enabled:
        example_questions.append(
            "Search the web for average software engineer salary in 2024 and compare to our Engineering department"
        )

    for q in example_questions:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.pending_question = q

    st.divider()

    # Conversation memory display
    if st.session_state.messages:
        st.markdown("**Conversation history**")
        st.caption(f"{len([m for m in st.session_state.messages if m['role'] == 'user'])} questions asked")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        reset_agent()
        st.rerun()

    st.divider()
    st.caption(f"Session: `{st.session_state.thread_id[:8]}...`")


# ── Main chat area ────────────────────────────────────────────────────────────

st.title("Workforce AI Agent")
st.caption("Ask anything about the workforce database — salaries, departments, headcount, contractors.")

# Render all previous messages without CoT trace
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Show CoT trace only for the latest assistant response
if st.session_state.latest_steps and st.session_state.messages:
    if st.session_state.messages[-1]["role"] == "assistant":
        render_cot_trace(st.session_state.latest_steps)

# Handle sidebar example button clicks
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.latest_steps = []
    with st.chat_message("user"):
        st.write(question)
    process_question(question)

# Chat input
if question := st.chat_input("Ask about the workforce..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.latest_steps = []
    with st.chat_message("user"):
        st.write(question)
    process_question(question)