<div align="center">

# 🔬 AI Research Assistant

### Multi-Agent AI System · LangGraph · RAG · MCP · FastAPI · Streamlit

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-FF6B35?style=for-the-badge)](https://langchain-ai.github.io/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

*Bootcamp Capstone Project — Built with LangChain, LangGraph, FAISS, MCP Servers, and Live APIs*

</div>

---

## 📌 What Is This?

The **AI Research Assistant** is a production-grade multi-agent AI system that answers complex research questions by intelligently combining information from multiple sources simultaneously:

- 📄 **Your own documents** (PDFs, TXT, Markdown) via a FAISS vector database
- 📰 **Live news articles** via NewsAPI
- 📚 **Academic books** via Open Library API
- 🗂️ **Local research notes** via Filesystem MCP Server
- 🗄️ **Session history** via SQLite MCP Server

Three specialized AI agents collaborate inside a LangGraph state machine to plan, retrieve, and synthesize a comprehensive answer — all served through a beautiful Streamlit UI backed by a FastAPI REST API.

---

## 🎯 Problem & Users

| | |
|---|---|
| **Problem** | Researchers and students waste hours manually searching across papers, news, and books to answer a single question |
| **End Users** | Students, researchers, analysts, and knowledge workers who need fast, multi-source answers |
| **Solution** | An agentic AI that autonomously searches all sources in parallel and synthesizes a cited, structured response |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI  (port 8501)                     │
│   Chat · History · Summary · Document Upload                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST
┌──────────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend  (port 8000)                   │
│   /query · /history · /summary · /add-document · /health        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   LangGraph Orchestrator                         │
│                                                                  │
│  check_query → [clarify?]                                        │
│       ↓                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────┐        │
│  │ Planner  │───▶│  Retriever   │───▶│  Synthesizer    │        │
│  │  Agent   │    │    Agent     │    │     Agent       │        │
│  └──────────┘    └──────────────┘    └─────────────────┘        │
│  Breaks query    RAG + APIs +        Writes cited answer         │
│  into plan       MCP reads           + saves to MCP             │
└──────────────────────────────────────────────────────────────────┘
          │                  │                    │
   ┌──────┴──────┐   ┌───────┴───────┐   ┌───────┴───────┐
   │  FAISS      │   │  NewsAPI      │   │  Open Library │
   │  Vector DB  │   │  (live news)  │   │  API (books)  │
   └─────────────┘   └───────────────┘   └───────────────┘
          │                                      │
   ┌──────┴──────┐                       ┌───────┴───────┐
   │ Filesystem  │                       │  SQLite MCP   │
   │ MCP Server  │                       │  (sessions)   │
   └─────────────┘                       └───────────────┘
```

---

## 🤖 The Three Agents

### Agent 1 — Planner Agent (`agents/planner_agent.py`)
Receives the raw user query and uses GPT-4o-mini to produce a structured JSON research plan. Decides which sources to activate, generates focused search terms, and breaks the query into sub-questions.

### Agent 2 — Retriever Agent (`agents/retriever_agent.py`)
Executes the plan in full. Searches the FAISS vector store for relevant document chunks, fetches live news articles, searches academic books, and reads local research notes — all in one pass.

### Agent 3 — Synthesizer Agent (`agents/synthesizer_agent.py`)
Takes every piece of retrieved context and writes a comprehensive, cited, well-structured final answer. Also persists the session to SQLite and appends a note to the filesystem via MCP.

---

## 🔀 LangGraph Workflow

```
START
  │
  ▼
check_query ──(too vague?)──▶ clarify ──▶ END
  │
  ▼
planner ──(error?)──▶ error ──▶ END
  │
  ▼
retriever ──(error?)──▶ error ──▶ END
  │
  ▼
synthesizer ──(error?)──▶ error ──▶ END
  │
  ▼
END
```

Every node reads from and writes to a shared `ResearchState` TypedDict. Conditional edges route based on error flags and query validation results.

---

## 🛠️ MCP Servers

| Server | File | What It Does |
|--------|------|--------------|
| **Filesystem MCP** | `mcp_tools/filesystem_mcp.py` | Read/write local research notes in `data/local/` |
| **SQLite MCP** | `mcp_tools/sqlite_mcp.py` | Store every research session, log sources used, enable history search |

---

## 🌐 External APIs

| API | File | Purpose | Key Required? |
|-----|------|---------|---------------|
| **NewsAPI** | `api_tools/news_api.py` | Fetch recent news articles on any topic | ✅ Free at newsapi.org |
| **Open Library** | `api_tools/open_library_api.py` | Search academic books by subject | ❌ No key needed |

---

## 💾 Data Sources

| Source | Type | Location |
|--------|------|----------|
| Local `.txt` / `.md` / `.pdf` documents | Local | `data/docs/` |
| SQLite research session database | Local | `data/local/knowledge.db` |
| NewsAPI live articles | Remote | REST API |
| Open Library book catalog | Remote | REST API |

---

## 🧠 Memory System

| Memory Type | Class | Purpose |
|-------------|-------|---------|
| **Buffer Memory** | `ChatMessageHistory` | Stores exact recent conversation turns |
| **Summary Memory** | GPT-4o-mini summarization | Compresses long histories into a running summary |

Both are managed by `memory/memory_manager.py` and injected into every agent prompt.

---

## 📁 Project Structure

```
research-assistant/
│
├── main.py                    ← CLI entry point
│
├── api/
│   └── server.py              ← FastAPI REST backend
│
├── ui/
│   └── app.py                 ← Streamlit frontend
│
├── agents/
│   ├── planner_agent.py       ← Agent 1: Query planning
│   ├── retriever_agent.py     ← Agent 2: Multi-source retrieval
│   └── synthesizer_agent.py   ← Agent 3: Answer synthesis
│
├── graph/
│   ├── state.py               ← LangGraph ResearchState TypedDict
│   └── workflow.py            ← State graph with nodes & edges
│
├── memory/
│   └── memory_manager.py      ← Buffer + Summary memory
│
├── retrieval/
│   ├── document_loader.py     ← Loads .txt / .md / .pdf files
│   ├── chunker.py             ← RecursiveCharacterTextSplitter
│   └── vector_store.py        ← FAISS build / load / search
│
├── mcp_tools/
│   ├── filesystem_mcp.py      ← MCP #1: Local file operations
│   └── sqlite_mcp.py          ← MCP #2: Session database
│
├── api_tools/
│   ├── news_api.py            ← NewsAPI client
│   └── open_library_api.py    ← Open Library client
│
├── config/
│   └── settings.py            ← Env loading & typed constants
│
├── data/
│   ├── docs/                  ← Your documents for RAG
│   ├── local/                 ← Auto-generated notes & SQLite DB
│   └── vector_store/          ← FAISS index (auto-generated)
│
├── utils/
│   └── helpers.py             ← Rich terminal formatting
│
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## ✅ Bootcamp Requirements Checklist

| Requirement | Implementation | File |
|-------------|---------------|------|
| `ChatOpenAI` | GPT-4o-mini for all agents | `agents/*.py` |
| `PromptTemplate` | LCEL prompt chains | `agents/*.py` |
| LLM Chain | `prompt \| llm \| parser` | `agents/*.py` |
| Buffer Memory | `ChatMessageHistory` | `memory/memory_manager.py` |
| Summary Memory | GPT summarization loop | `memory/memory_manager.py` |
| Embeddings | `OpenAIEmbeddings` | `retrieval/vector_store.py` |
| Chunking | `RecursiveCharacterTextSplitter` | `retrieval/chunker.py` |
| Vector DB | FAISS | `retrieval/vector_store.py` |
| Agent 1 | Planner Agent | `agents/planner_agent.py` |
| Agent 2 | Retriever Agent | `agents/retriever_agent.py` |
| Agent 3 | Synthesizer Agent | `agents/synthesizer_agent.py` |
| LangGraph | StateGraph + conditional edges | `graph/workflow.py` |
| MCP Server #1 | Filesystem MCP | `mcp_tools/filesystem_mcp.py` |
| MCP Server #2 | SQLite MCP | `mcp_tools/sqlite_mcp.py` |
| External API #1 | NewsAPI | `api_tools/news_api.py` |
| External API #2 | Open Library | `api_tools/open_library_api.py` |
| Local Data Source | TXT docs + SQLite | `data/` |
| Remote Data Source | NewsAPI + Open Library | `api_tools/` |
| FastAPI | REST backend | `api/server.py` |
| Streamlit UI | Full chat interface | `ui/app.py` |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai-research-assistant.git
cd ai-research-assistant

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5a. Run CLI only
python main.py

# 5b. Run full UI (two terminals)
uvicorn api.server:app --reload --port 8000   # Terminal 1
streamlit run ui/app.py                        # Terminal 2
# Open http://localhost:8501
```

---

## 🖥️ UI Features

| Tab | Feature |
|-----|---------|
| 💬 Chat | Bubble chat UI, source tags per answer, Planner Agent plan viewer |
| 📜 History | All past sessions from SQLite, searchable, re-ask button |
| 📋 Summary | Live AI summary + recent turns side by side |
| 📁 Upload | Drag & drop docs into the knowledge base, auto-rebuilds FAISS |
| 💡 Sidebar | Quick example queries, session stats, API status indicator |

---

## 📄 License

MIT License — free to use, modify, and distribute.