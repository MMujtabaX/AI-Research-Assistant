# 🚀 Setup & Run Guide
## AI Research Assistant — Complete Step-by-Step Instructions

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [GitHub Repository Setup](#2-github-repository-setup)
3. [Clone & Open in VS Code](#3-clone--open-in-vs-code)
4. [Python Environment](#4-python-environment)
5. [Install Dependencies](#5-install-dependencies)
6. [Configure API Keys](#6-configure-api-keys)
7. [Project File Structure](#7-project-file-structure)
8. [How to Run](#8-how-to-run)
9. [Step-by-Step Flow Explained](#9-step-by-step-flow-explained)
10. [Streamlit UI Guide](#10-streamlit-ui-guide)
11. [FastAPI Endpoints](#11-fastapi-endpoints)
12. [Example Queries](#12-example-queries)
13. [Add Your Own Documents](#13-add-your-own-documents)
14. [Troubleshooting](#14-troubleshooting)
15. [Extending the Project](#15-extending-the-project)

---

## 1. Prerequisites

Install these before starting:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | https://python.org/downloads |
| Git | Any | https://git-scm.com/downloads |
| VS Code | Any | https://code.visualstudio.com |

**Check your versions:**
```bash
python --version    # should show 3.11+
git --version
```

**Recommended VS Code extensions:**
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)

---

## 2. GitHub Repository Setup

### Create the repo on GitHub
1. Go to https://github.com → click **New**
2. Name: `ai-research-assistant`
3. Set visibility (Public or Private)
4. ✅ Add README, select Python `.gitignore`
5. Click **Create repository**

### Push your local project to GitHub
```bash
cd ai-research-assistant

git init
git remote add origin https://github.com/YOUR_USERNAME/ai-research-assistant.git
git add .
git commit -m "Initial commit: Multi-agent AI research assistant"
git push -u origin main
```

---

## 3. Clone & Open in VS Code

```bash
git clone https://github.com/YOUR_USERNAME/ai-research-assistant.git
cd ai-research-assistant
code .
```

---

## 4. Python Environment

Always use a virtual environment to keep dependencies isolated.

**Create it:**
```bash
# Windows
python -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

**Activate it:**
```bash
# Windows Command Prompt
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

**Select interpreter in VS Code:**
1. Press `Ctrl+Shift+P`
2. Type `Python: Select Interpreter`
3. Choose `./.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)

---

## 5. Install Dependencies

With your virtual environment **activated**:

```bash
pip install -r requirements.txt
```

This installs all packages including:

| Package | Purpose |
|---------|---------|
| `langchain`, `langchain-openai`, `langchain-community` | LangChain core |
| `langchain-core`, `langchain-text-splitters` | LangChain utilities |
| `langgraph` | Multi-agent state machine |
| `faiss-cpu` | Vector similarity search |
| `pypdf` | PDF document loading |
| `python-dotenv` | Load `.env` file |
| `requests`, `httpx` | HTTP calls to APIs |
| `tiktoken` | Token counting |
| `rich` | Beautiful terminal output |
| `fastapi`, `uvicorn` | REST API backend |
| `streamlit` | Web UI frontend |
| `python-multipart` | File upload support |

> Takes 1–3 minutes on first install.

---

## 6. Configure API Keys

### Step 1 — Create your `.env` file

**Windows PowerShell:**
```powershell
@"
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
NEWS_API_KEY=YOUR_NEWS_KEY_HERE
LOCAL_DATA_DIR=./data/local
DOCS_DIR=./data/docs
VECTOR_STORE_DIR=./data/vector_store
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
"@ | Out-File -FilePath .env -Encoding utf8
```

**macOS / Linux:**
```bash
cp .env.example .env
# Then edit .env in VS Code and fill in your keys
```

### Step 2 — Get your API keys

**OpenAI API Key (Required)**
1. Go to https://platform.openai.com/api-keys
2. Click **+ Create new secret key**
3. Copy the key (starts with `sk-proj-`)
4. Paste it into `.env` as `OPENAI_API_KEY=sk-proj-...`
5. Make sure your account has credit balance

**NewsAPI Key (Optional — free)**
1. Go to https://newsapi.org/register
2. Register with your email
3. Copy your API key from the dashboard
4. Paste into `.env` as `NEWS_API_KEY=...`
5. Free tier: 100 requests/day
6. If left empty, the system uses mock news results

**Open Library API**
- ✅ Completely free, no key needed

### Step 3 — Verify your `.env`

```bash
# Should print your actual key (not the placeholder)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"
```

---

## 7. Project File Structure

```
research-assistant/
│
├── 📄 main.py                    CLI entry point — boots system, runs chat loop
├── 📄 requirements.txt           All Python dependencies
├── 📄 .env                       Your API keys (never commit this!)
├── 📄 .env.example               Template for .env
├── 📄 .gitignore                 Excludes .env, venv, vector store from Git
│
├── 📁 api/
│   └── server.py                 FastAPI REST backend (port 8000)
│                                 Exposes /query, /history, /health etc.
│
├── 📁 ui/
│   └── app.py                    Streamlit frontend (port 8501)
│                                 Chat UI, History, Summary, Upload tabs
│
├── 📁 agents/
│   ├── planner_agent.py          Agent 1 — reads query, builds JSON plan
│   ├── retriever_agent.py        Agent 2 — executes plan across all sources
│   └── synthesizer_agent.py      Agent 3 — writes final cited answer
│
├── 📁 graph/
│   ├── state.py                  ResearchState TypedDict (shared between nodes)
│   └── workflow.py               LangGraph graph: nodes, edges, routing logic
│
├── 📁 memory/
│   └── memory_manager.py         Buffer memory + GPT summary memory
│
├── 📁 retrieval/
│   ├── document_loader.py        Loads .txt / .md / .pdf from data/docs/
│   ├── chunker.py                Splits docs into 500-char overlapping chunks
│   └── vector_store.py           FAISS build / load / similarity search
│
├── 📁 mcp_tools/
│   ├── filesystem_mcp.py         MCP Server 1: read/write local files
│   └── sqlite_mcp.py             MCP Server 2: save/query research sessions
│
├── 📁 api_tools/
│   ├── news_api.py               NewsAPI client (recent articles)
│   └── open_library_api.py       Open Library client (books search)
│
├── 📁 config/
│   └── settings.py               Loads .env, exposes typed constants
│
├── 📁 data/
│   ├── docs/                     ← PUT YOUR DOCUMENTS HERE for RAG
│   │   ├── ai_fundamentals.txt   Sample doc (included)
│   │   └── research_methods.txt  Sample doc (included)
│   ├── local/
│   │   ├── research_notes.txt    Auto-populated by Synthesizer Agent
│   │   └── knowledge.db          SQLite database (auto-created)
│   └── vector_store/             FAISS index files (auto-created)
│
└── 📁 utils/
    └── helpers.py                Rich terminal formatting helpers
```

---

## 8. How to Run

You have two options: **CLI mode** (simple) or **Full UI mode** (impressive).

---

### Option A — CLI Mode (Terminal only)

Good for testing and development.

```bash
python main.py
```

**Available commands inside the chat:**

| Type | Action |
|------|--------|
| Any question | Run a full research query |
| `history` | Show recent sessions from SQLite |
| `summary` | Show the compressed conversation summary |
| `clear` | Reset conversation memory |
| `quit` | Exit |

---

### Option B — Full UI Mode (Recommended)

Requires **two terminals** open at the same time, both inside the project folder with `.venv` activated.

**Terminal 1 — Start the FastAPI backend:**
```bash
uvicorn api.server:app --reload --port 8000
```

Wait until you see:
```
✅ System ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

> The first run takes longer because it builds the FAISS vector store (calls OpenAI Embeddings API).

**Terminal 2 — Start the Streamlit frontend:**
```bash
streamlit run ui/app.py
```

Then open your browser: **http://localhost:8501**

---

### Stopping the servers

```bash
# Press Ctrl+C in each terminal
```

---

## 9. Step-by-Step Flow Explained

Here is exactly what happens when you type a query:

```
You type: "What are recent breakthroughs in quantum computing?"
```

### Step 1 — FastAPI receives the request
`POST /query` → `api/server.py` validates the request and builds the initial `ResearchState`.

### Step 2 — LangGraph: `check_query` node
Checks if the query is valid (not too short, not just "hi"). If too vague → routes to `clarify` node which asks for more detail.

### Step 3 — LangGraph: `planner` node → PlannerAgent
Sends the query to GPT-4o-mini with a prompt asking for a JSON plan:
```json
{
  "search_terms": ["quantum computing breakthroughs", "quantum computing 2024"],
  "use_local_docs": true,
  "use_news_api": true,
  "use_books_api": true,
  "sub_questions": [
    "What is quantum computing?",
    "What are the latest breakthroughs?"
  ],
  "reasoning": "Topic needs both foundational docs and recent news"
}
```

### Step 4 — LangGraph: `retriever` node → RetrieverAgent
Executes every enabled source in the plan:

```
[FAISS]        → similarity_search("quantum computing breakthroughs")
                 → returns 4 most relevant text chunks from your docs

[NewsAPI]      → GET newsapi.org/v2/everything?q=quantum+computing
                 → returns 4 recent articles with title, description, URL

[Open Library] → GET openlibrary.org/search.json?q=quantum+computing
                 → returns 4 books with title, author, year, subjects

[Filesystem MCP] → reads data/local/research_notes.txt
                   → returns your saved research notes
```

### Step 5 — LangGraph: `synthesizer` node → SynthesizerAgent
Passes ALL context to GPT-4o-mini with a prompt to write a comprehensive answer.

Then saves the session:
```
[SQLite MCP]     → INSERT INTO research_sessions (query, answer, sources)
[Filesystem MCP] → appends timestamped note to research_notes.txt
```

### Step 6 — Memory Update
```
BufferMemory  → stores the exact turn (query + answer)
SummaryMemory → GPT compresses conversation history into running summary
```

### Step 7 — Response returned
FastAPI sends back `{ query, answer, sources, plan }` → Streamlit renders it as a chat bubble with source tags.

---

## 10. Streamlit UI Guide

| Tab | What's There |
|-----|-------------|
| **💬 Chat** | Main chat interface. Bubbles for you and AI. Each answer shows source tags (which APIs/docs were used). Click "View Research Plan" to see the Planner Agent's JSON output. |
| **📜 History** | All past research sessions stored in SQLite. Search by keyword. Click "Re-ask" to send any old query again. |
| **📋 Summary** | Left: AI-generated compressed summary of your session. Right: Raw recent conversation turns. |
| **📁 Upload** | Drag and drop `.txt`, `.md`, or `.pdf` files. They get chunked, embedded, and added to FAISS automatically. Also has a "Rebuild" button. |
| **Sidebar** | API status indicator, navigation buttons, session stats, and 5 example quick queries that auto-fill the chat box. |

---

## 11. FastAPI Endpoints

The API runs at `http://localhost:8000`. You can test it at **http://localhost:8000/docs** (auto-generated Swagger UI).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check if system is ready |
| `POST` | `/query` | Run a research query |
| `GET` | `/history?limit=10` | Get recent sessions |
| `GET` | `/summary` | Get conversation summary |
| `POST` | `/clear-memory` | Reset memory |
| `POST` | `/add-document` | Upload a file to knowledge base |
| `DELETE` | `/vector-store` | Rebuild FAISS index |
| `GET` | `/search-history?keyword=X` | Search past sessions |

**Test with curl:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

---

## 12. Example Queries

```
# Tests RAG (local documents)
What is the transformer architecture?
How does FAISS work?
What are the key components of a neural network?

# Tests News API (recent events)
What are the latest AI research breakthroughs?
Recent developments in large language models

# Tests Open Library (books)
What are good books to learn about machine learning?
Recommend books on research methodology

# Tests multi-source (everything activates)
Explain deep learning and its recent applications
What is quantum computing and what progress has been made?

# Tests memory (ask these in sequence)
What is RAG?
Can you explain more about the vector database part?
Summarize what we just discussed
```

---

## 13. Add Your Own Documents

1. Drop any `.txt`, `.md`, or `.pdf` file into `data/docs/`

2. Delete the old vector store so it rebuilds:
```bash
# Windows
rmdir /s /q data\vector_store

# macOS / Linux
rm -rf data/vector_store/
```

3. Restart the server:
```bash
uvicorn api.server:app --reload --port 8000
```

Or use the **Upload tab** in the Streamlit UI — it handles everything automatically.

---

## 14. Troubleshooting

### `OPENAI_API_KEY is not set`
```powershell
# Check what's in your .env
Get-Content .env

# Verify Python can read it
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```
Make sure each variable is on its **own line** with no spaces around `=`.

---

### `ModuleNotFoundError`
```bash
# Make sure venv is activated (you should see (.venv))
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

---

### `No chunks provided to build vector store`
`data/docs/` is empty or missing. The project ships with two sample docs already in that folder. If they're missing, create them or add your own `.txt` files.

---

### Streamlit sidebar not showing
The sidebar is set to `initial_sidebar_state="expanded"`. If it collapses, look for the **purple arrow tab** on the left edge of the screen — click it to reopen.

---

### `Cannot connect to API`
Make sure the FastAPI server is running in Terminal 1:
```bash
uvicorn api.server:app --reload --port 8000
```
The green dot in the Streamlit sidebar will turn on once it detects the API.

---

### Port already in use
```bash
# Use a different port
uvicorn api.server:app --reload --port 8001

# Then update API_BASE in ui/app.py line 16:
API_BASE = "http://localhost:8001"
```

---

### FAISS index seems outdated after adding docs
```bash
rmdir /s /q data\vector_store   # Windows
rm -rf data/vector_store/        # macOS/Linux
# Restart the server — it rebuilds automatically
```

---

## 15. Extending the Project

### Add a third API (Wikipedia — free, no key)
Create `api_tools/wikipedia_api.py`:
```python
import requests

def search_wikipedia(query: str) -> str:
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
    r = requests.get(url, timeout=5)
    return r.json().get("extract", "No Wikipedia article found.")
```
Then call it in `agents/retriever_agent.py`.

### Add streaming responses
Replace `app.invoke()` in FastAPI with `app.astream()` and use Streamlit's `st.write_stream()`.

### Deploy to the cloud
- **Backend:** Deploy FastAPI to Railway, Render, or AWS EC2
- **Frontend:** Deploy Streamlit to Streamlit Community Cloud (free)
- **Vector store:** Replace FAISS with Pinecone for persistent cloud storage

### Add authentication
```bash
pip install python-jose passlib
```
Add JWT auth to FastAPI endpoints.

---

## ⚡ Quick Reference Card

```bash
# First-time setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Edit .env with your OPENAI_API_KEY

# Run CLI
python main.py

# Run full UI (two terminals)
uvicorn api.server:app --reload --port 8000   # Terminal 1
streamlit run ui/app.py                        # Terminal 2
# → Open http://localhost:8501

# Reset vector store (after adding new docs)
rmdir /s /q data\vector_store    # Windows
rm -rf data/vector_store/         # macOS/Linux

# Push to GitHub
git add .
git commit -m "your message"
git push
```