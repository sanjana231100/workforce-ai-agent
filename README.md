---
title: Workforce AI Agent
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---
# 🤖 Workforce AI Agent

An intelligent ReAct agent that reasons over multiple steps to answer complex workforce questions using a local SQLite database, live web search, and a calculator.

Built with **Python · LangChain · SQLite · DuckDuckGo · Streamlit · HuggingFace Spaces**.

---

## 💡 Example Query

> "How many contractors in the Engineering department earn above $80k, and what percentage is that of total headcount?"

The agent will:
1. Query the local SQLite workforce database for contractors in Engineering above $80k
2. Query total headcount
3. Calculate the percentage
4. Return a complete, reasoned answer with a full chain-of-thought trace

---

## 🏗️ Architecture

```
User → Streamlit Chat UI → LangChain AgentExecutor (ReAct loop)
                                    ↕
                         ┌──────────────────────┐
                         │  Tool 1: DuckDuckGo   │ ← web search
                         │  Tool 2: SQL Query    │ ← workforce.db
                         │  Tool 3: Calculator   │ ← math
                         └──────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/sanjana231100/workforce-ai-agent.git
cd workforce-ai-agent
```

### 2. Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. Seed the database
```bash
python seed_db.py
```

### 6. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
workforce-ai-agent/
├── app.py              # Streamlit chat UI
├── agent.py            # LangChain AgentExecutor setup
├── tools.py            # 3 tool definitions (search, SQL, calculator)
├── seed_db.py          # Script to generate workforce.db
├── workforce.db        # SQLite database (200 fake employees)
├── utils/
│   ├── db_utils.py     # Database connection helper
│   └── formatting.py   # Result formatting helpers
├── .streamlit/
│   └── config.toml     # Streamlit theme settings
├── requirements.txt
├── .gitignore
└── Dockerfile          # For HuggingFace Spaces deployment
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Agent framework | LangChain (LCEL, AgentExecutor) |
| LLM | OpenAI gpt-3.5-turbo |
| Web search | DuckDuckGo (free, no API key) |
| Database | SQLite (built into Python) |
| Deployment | HuggingFace Spaces (Docker) |

---

## 🌐 Live Demo

Deployed on HuggingFace Spaces: https://huggingface.co/spaces/sanjana231100/workforce-ai-agent

---

## 👩‍💻 Author

**Sanjana** · [github.com/sanjana231100](https://github.com/sanjana231100)