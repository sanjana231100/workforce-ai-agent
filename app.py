import streamlit as st
import uuid
from agent import create_agent, run_agent

st.set_page_config(
    page_title="Workforce AI Agent",
    page_icon="🤖",
    layout="wide",
)

# ── Session state initialisation ──────────────────────────────────────────────

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Tracks the steps for the most recent response only
if "latest_steps" not in st.session_state:
    st.session_state.latest_steps = []


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

    # Save message without steps — old messages never show the trace
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

    # Store steps separately — only the latest response shows them
    st.session_state.latest_steps = steps


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 Workforce AI Agent")
    st.caption("Powered by LangGraph + Groq + SQLite")

    st.divider()

    st.markdown("**Example questions**")
    example_questions = [
        "How many contractors in Engineering earn above $80k?",
        "What is the average salary by department?",
        "List the top 5 highest paid employees",
        "How many employees were hired in the last 2 years?",
        "Which department has the most Outstanding performers?",
        "What percentage of staff are contractors?",
    ]

    for q in example_questions:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.pending_question = q

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.latest_steps = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.agent = create_agent()
        st.rerun()

    st.divider()
    st.caption(f"Session: `{st.session_state.thread_id[:8]}...`")


# ── Main chat area ────────────────────────────────────────────────────────────

st.title("Workforce AI Agent")
st.caption("Ask anything about the workforce database — salaries, departments, headcount, contractors.")

# Render all previous messages — no CoT trace for old messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Show CoT trace only for the latest assistant response
if st.session_state.latest_steps and st.session_state.messages:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "assistant":
        render_cot_trace(st.session_state.latest_steps)

# Handle sidebar example button clicks
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.latest_steps = []
    with st.chat_message("user"):
        st.write(question)
    process_question(question)

# Chat input at the bottom
if question := st.chat_input("Ask about the workforce..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.latest_steps = []
    with st.chat_message("user"):
        st.write(question)
    process_question(question)