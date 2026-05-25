# 🚀 Complete Step-by-Step Setup & Run Guide
## AI Research Assistant — Multi-Agent Capstone Project

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [GitHub Repository Setup](#2-github-repository-setup)
3. [Clone & Open in VS Code](#3-clone--open-in-vs-code)
4. [Python Environment Setup](#4-python-environment-setup)
5. [Install Dependencies](#5-install-dependencies)
6. [Configure API Keys](#6-configure-api-keys)
7. [Understand the File Structure](#7-understand-the-file-structure)
8. [Run the Application](#8-run-the-application)
9. [How the System Works — Step by Step Flow](#9-how-the-system-works--step-by-step-flow)
10. [Example Queries to Try](#10-example-queries-to-try)
11. [Troubleshooting](#11-troubleshooting)
12. [Extending the Project](#12-extending-the-project)
13. [How Each Requirement is Met](#13-how-each-requirement-is-met)

---

## 1. Prerequisites

Before starting, make sure you have these installed on your computer:

### 1.1 Python 3.11+
```bash
# Check your Python version
python --version
# or
python3 --version
```
If not installed: https://www.python.org/downloads/

### 1.2 Git
```bash
git --version
```
If not installed: https://git-scm.com/downloads

### 1.3 VS Code
Download from: https://code.visualstudio.com/

### 1.4 VS Code Extensions (recommended)
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **GitLens** (optional but helpful)

---

## 2. GitHub Repository Setup

### 2.1 Create a new GitHub repository

1. Go to https://github.com → Click **New** (green button)
2. Repository name: `ai-research-assistant`
3. Description: `Multi-Agent AI Research Assistant — Bootcamp Capstone`
4. Set to **Public** (or Private — your choice)
5. ✅ Check **Add a README file**
6. **.gitignore**: select `Python`
7. Click **Create repository**

### 2.2 Push the project code

After you download the project files, push them to GitHub:

```bash
# Navigate into the project folder
cd ai-research-assistant

# Initialize git (if not already done)
git init

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-research-assistant.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: Multi-agent AI research assistant"

# Push to GitHub
git push -u origin main
```

---

## 3. Clone & Open in VS Code

```bash
# Clone the repository (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/ai-research-assistant.git

# Navigate into the folder
cd ai-research-assistant

# Open in VS Code
code .
```

After VS Code opens, you should see the full project structure in the Explorer panel.

---

## 4. Python Environment Setup

**Always use a virtual environment** to avoid dependency conflicts.

### 4.1 Create the virtual environment

Open the **VS Code Terminal** (`Ctrl + `` ` `` ` or `Terminal → New Terminal`):

```bash
# Windows
python -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

### 4.2 Activate the virtual environment

```bash
# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### 4.3 Select the interpreter in VS Code

1. Press `Ctrl+Shift+P` → type `Python: Select Interpreter`
2. Choose the one that says `.venv` (e.g., `./.venv/bin/python`)

---

## 5. Install Dependencies

With your virtual environment **activated**:

```bash
pip install -r requirements.txt
```

This installs:
- `langchain`, `langchain-openai`, `langchain-community` — LangChain core
- `langgraph` — State machine orchestration
- `faiss-cpu` — Vector similarity search
- `pypdf` — PDF loading
- `python-dotenv` — Environment variable management
- `requests`, `httpx` — HTTP calls to APIs
- `tiktoken` — Token counting for OpenAI
- `rich` — Beautiful terminal output

**Expected output:** Many packages installing. Takes 1-3 minutes.

---

## 6. Configure API Keys

### 6.1 Copy the example file

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 6.2 Edit the .env file

Open `.env` in VS Code and fill in your keys:

```env
# Required
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional (news search works without it but gives mock results)
NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxx

# These stay as-is (paths and model settings)
LOCAL_DATA_DIR=./data/local
DOCS_DIR=./data/docs
VECTOR_STORE_DIR=./data/vector_store
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

### 6.3 Get your API Keys

**OpenAI API Key (Required)**
1. Go to https://platform.openai.com/api-keys
2. Click **+ Create new secret key**
3. Copy the key (starts with `sk-`)
4. Make sure your account has credits

**NewsAPI Key (Optional — free)**
1. Go to https://newsapi.org/register
2. Register with email
3. Copy your API key from the dashboard
4. Free tier: 100 requests/day

**Open Library API**
- ✅ No key needed! Completely free and open.

---

## 7. Understand the File Structure

Here is every file explained:

```
research-assistant/
│
├── 📄 main.py                    ← START HERE. The entry point.
│                                   Boots the system, runs the chat loop.
│
├── 📄 requirements.txt           ← All Python package dependencies
├── 📄 .env.example               ← Template for your API keys
├── 📄 .env                       ← Your actual API keys (DO NOT commit this!)
├── 📄 .gitignore                 ← Files Git ignores (includes .env)
├── 📄 README.md                  ← Project overview
│
├── 📁 config/
│   └── settings.py               ← Loads .env, exposes typed constants
│                                   (OPENAI_API_KEY, model names, paths)
│
├── 📁 agents/                    ← THE 3 SPECIALIZED AGENTS
│   ├── planner_agent.py          ← Agent 1: Reads query, makes a plan
│   │                               Decides: use RAG? use News? use Books?
│   ├── retriever_agent.py        ← Agent 2: Executes the plan
│   │                               Searches vector DB + APIs + local notes
│   └── synthesizer_agent.py      ← Agent 3: Writes the final answer
│                                   Saves results to SQLite + filesystem
│
├── 📁 graph/                     ← LANGGRAPH WORKFLOW
│   ├── state.py                  ← The shared state TypedDict that flows
│   │                               between all nodes
│   └── workflow.py               ← The graph: nodes, edges, routing logic
│
├── 📁 memory/
│   └── memory_manager.py         ← Buffer Memory + Summary Memory
│                                   Keeps conversation context
│
├── 📁 retrieval/                 ← RAG PIPELINE
│   ├── document_loader.py        ← Loads .txt, .md, .pdf from data/docs/
│   ├── chunker.py                ← Splits docs into 500-char overlapping chunks
│   └── vector_store.py           ← FAISS build/load/search
│
├── 📁 mcp_tools/                 ← MCP SERVER WRAPPERS
│   ├── filesystem_mcp.py         ← MCP #1: Read/write local files
│   └── sqlite_mcp.py             ← MCP #2: Store sessions in SQLite DB
│
├── 📁 api_tools/                 ← EXTERNAL API CLIENTS
│   ├── news_api.py               ← API #1: Recent news via NewsAPI
│   └── open_library_api.py       ← API #2: Book search via Open Library
│
├── 📁 data/
│   ├── local/
│   │   ├── research_notes.txt    ← Auto-populated by the system
│   │   └── knowledge.db          ← SQLite DB (auto-created on first run)
│   ├── docs/
│   │   ├── ai_fundamentals.txt   ← Sample document for RAG
│   │   └── research_methods.txt  ← Sample document for RAG
│   └── vector_store/             ← FAISS index saved here (auto-created)
│
└── 📁 utils/
    └── helpers.py                ← Pretty printing with Rich library
```

---

## 8. Run the Application

Make sure your virtual environment is activated and `.env` is configured.

```bash
python main.py
```

### First Run

The first run will:
1. Load the documents from `data/docs/`
2. Split them into chunks
3. Call OpenAI Embeddings API to create vectors (~10 seconds, costs a tiny amount)
4. Save the FAISS index to `data/vector_store/`
5. Start the chat interface

**Subsequent runs** are faster — the FAISS index is loaded from disk.

### Using the Chat Interface

```
🔍 You: What is retrieval-augmented generation?

⏳ Researching...

╭─ 🤖 Research Assistant ───────────────────────────────────╮
│                                                            │
│  ## Retrieval-Augmented Generation (RAG)                  │
│                                                            │
│  RAG is a technique that combines...                       │
│  ...                                                       │
│  ### Key Takeaways                                         │
│  • RAG grounds LLM responses in factual sources           │
│  ...                                                       │
╰────────────────────────────────────────────────────────────╯

📡 Sources consulted: local_vector_store, news_api, open_library_api
```

### Available Commands

| Command | Action |
|---------|--------|
| Any question | Run a research query |
| `clear` | Reset conversation memory |
| `history` | Show past research sessions from SQLite |
| `summary` | Show the compressed conversation summary |
| `quit` or `exit` | Exit the program |

---

## 9. How the System Works — Step by Step Flow

Here is exactly what happens when you type a query:

### Step 1: `main.py` — Entry & State Creation
```
User types: "What is quantum computing and recent breakthroughs?"
  ↓
main.py creates ResearchState:
  {
    query: "What is quantum computing...",
    chat_history: "<last 3 turns from BufferMemory>",
    conversation_summary: "<compressed summary from SummaryMemory>",
    plan: None,
    context: None,
    final_answer: None
  }
```

### Step 2: LangGraph `check_query` Node
```
Validates the query:
  - Is it too short? → route to "clarify"
  - Is it a vague word like "hi"? → route to "clarify"
  - Otherwise → route to "planner"
```

### Step 3: LangGraph `planner` Node → PlannerAgent
```
PlannerAgent sends query to GPT-4o-mini with a prompt asking it to return JSON:
{
  "search_terms": ["quantum computing", "quantum breakthroughs 2024"],
  "use_local_docs": true,
  "use_news_api": true,
  "use_books_api": true,
  "sub_questions": [
    "What is quantum computing?",
    "What are recent quantum computing breakthroughs?"
  ],
  "reasoning": "Topic involves both foundational knowledge and recent events"
}
State updated: plan = {...}
```

### Step 4: LangGraph `retriever` Node → RetrieverAgent
```
RetrieverAgent executes the plan:

  [RAG] → search_vector_store("quantum computing")
           → returns 4 most similar text chunks from data/docs/

  [News] → newsapi.org/v2/everything?q=quantum+computing
           → returns 4 recent news articles

  [Books] → openlibrary.org/search.json?q=quantum+computing
            → returns 4 relevant books

  [Filesystem MCP] → reads data/local/research_notes.txt

State updated: context = {rag_results, news_text, books_text, local_notes, sources_used}
```

### Step 5: LangGraph `synthesizer` Node → SynthesizerAgent
```
SynthesizerAgent receives ALL context and sends to GPT-4o-mini:

  Prompt includes:
    - Original query
    - Sub-questions to address
    - RAG chunks
    - News articles
    - Book recommendations
    - Local notes
    - Recent chat history

  Model writes comprehensive answer with citations.

  Then: 
    [SQLite MCP] → saves session to knowledge.db
    [Filesystem MCP] → appends note to research_notes.txt

State updated: final_answer = "..."
```

### Step 6: Memory Update & Output
```
main.py:
  memory.save_turn(query, answer)
    → BufferMemory: stores raw turn
    → SummaryMemory: updates compressed summary

  Displays answer with Rich formatting
  Shows which sources were used
```

---

## 10. Example Queries to Try

Start simple, then go complex:

```
# Foundational AI knowledge (uses RAG heavily)
What is the transformer architecture?

# Recent news (uses News API heavily)
What are the latest developments in AI research?

# Books (uses Open Library heavily)
What are good books to learn about machine learning?

# Multi-source (uses everything)
Explain deep learning and what recent breakthroughs happened

# Research methodology
How do I conduct a proper literature review?

# Conversational follow-up (tests memory)
Tell me more about that last point
What did we just discuss? (tests summary memory)

# Command tests
history
summary
clear
```

---

## 11. Troubleshooting

### "OPENAI_API_KEY not set"
```bash
# Make sure .env exists
ls -la .env

# Check the key is there
cat .env | grep OPENAI
```

### "No module named 'langchain'"
```bash
# Make sure venv is activated (you should see (.venv))
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

# Reinstall
pip install -r requirements.txt
```

### "No chunks provided to build vector store"
This means `data/docs/` is empty.
- Add some `.txt` or `.pdf` files to `data/docs/`
- The project already includes `ai_fundamentals.txt` and `research_methods.txt`

### "NewsAPI returns mock results"
- Your `NEWS_API_KEY` in `.env` might be empty
- The system falls back to mock results automatically
- Get a free key at https://newsapi.org

### "FAISS index already exists but seems wrong"
Delete the vector store and rebuild:
```bash
# Delete the old index
rm -rf data/vector_store/

# Run again — it will rebuild
python main.py
```

### PowerShell execution policy error (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 12. Extending the Project

Here are ideas for making the project even more impressive:

### Add More Documents to RAG
Drop any `.txt`, `.md`, or `.pdf` files into `data/docs/`.
Delete `data/vector_store/` so it rebuilds the index.

### Add a Third API (e.g., Wikipedia)
Create `api_tools/wikipedia_api.py`:
```python
import requests
def search_wikipedia(query: str) -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    response = requests.get(url)
    return response.json().get("extract", "")
```

### Add a Web UI with Streamlit
```bash
pip install streamlit
```
Create `app.py` and run with `streamlit run app.py`

### Add a Third MCP Server (Notion or GitHub)
See the MCP registry at https://github.com/modelcontextprotocol/servers

### Export as a REST API with FastAPI
```bash
pip install fastapi uvicorn
```
Wrap `run_query()` in a FastAPI endpoint.

---

## 13. How Each Requirement is Met

| Requirement | File | Implementation |
|-------------|------|----------------|
| ChatOpenAI | `agents/*.py`, `memory/memory_manager.py` | `ChatOpenAI(model="gpt-4o-mini")` |
| PromptTemplate | `agents/*.py` | `PromptTemplate(input_variables=[...])` |
| LLMChain (modern) | `agents/*.py` | LCEL chain: `prompt | llm | parser` |
| ConversationBufferMemory | `memory/memory_manager.py` | `ConversationBufferMemory()` |
| Extra Memory Strategy | `memory/memory_manager.py` | `ConversationSummaryMemory()` |
| Embeddings | `retrieval/vector_store.py` | `OpenAIEmbeddings()` |
| Chunking | `retrieval/chunker.py` | `RecursiveCharacterTextSplitter()` |
| Vector DB | `retrieval/vector_store.py` | FAISS |
| 3 Agents | `agents/` | Planner, Retriever, Synthesizer |
| LangGraph | `graph/workflow.py` | `StateGraph` with 6 nodes + conditional edges |
| MCP Server #1 | `mcp_tools/filesystem_mcp.py` | Filesystem read/write/list |
| MCP Server #2 | `mcp_tools/sqlite_mcp.py` | SQLite session storage |
| External API #1 | `api_tools/news_api.py` | NewsAPI |
| External API #2 | `api_tools/open_library_api.py` | Open Library |
| Data Source #1 (local) | `data/docs/` | Local `.txt` documents |
| Data Source #2 (remote) | `api_tools/` | NewsAPI + Open Library remote calls |

---

## 📞 Quick Reference Card

```bash
# Setup (one time)
python3 -m venv .venv
source .venv/bin/activate       # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# → Edit .env and add OPENAI_API_KEY

# Run
python main.py

# Reset vector store (if you add new docs)
rm -rf data/vector_store/
python main.py

# Deactivate venv when done
deactivate
```
