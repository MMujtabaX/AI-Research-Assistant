# 🔬 AI Research Assistant — Multi-Agent System

> **Bootcamp Capstone Project** — Multi-Agent AI System with Memory, Retrieval, LangGraph, MCP, APIs, and Multi-Source Data

---

## 📌 Project Overview

### Problem Being Solved
Researchers, students, and analysts spend hours searching across multiple sources (papers, news, local notes, PDFs) to compile and synthesize information. This system automates that entire workflow using specialized AI agents.

### Who is the End User?
Students, researchers, and knowledge workers who need to quickly gather, summarize, and answer questions across multiple data sources.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│              LangGraph Orchestrator              │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Planner  │→ │Retriever │→ │  Synthesizer  │  │
│  │  Agent   │  │  Agent   │  │    Agent      │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│       │              │               │          │
│  Breaks query   RAG + Vector    Combines &      │
│  into tasks     DB search       responds        │
└─────────────────────────────────────────────────┘
         │              │
    MCP Servers      External APIs
  ┌──────────┐      ┌──────────────┐
  │Filesystem│      │ News API     │
  │  Server  │      │ Open Library │
  │ (notes)  │      │   API        │
  └──────────┘      └──────────────┘
```

---

## 📋 Requirements Checklist

| Requirement | Implementation |
|-------------|---------------|
| LangChain Foundations | `ChatOpenAI`, `PromptTemplate`, `LLMChain` |
| Memory (Buffer) | `ConversationBufferMemory` |
| Memory (Extra) | `ConversationSummaryMemory` |
| RAG Pipeline | FAISS + OpenAI Embeddings + text chunking |
| 3+ Agents | Planner, Retriever, Synthesizer |
| LangGraph | State graph with branching logic |
| 2+ MCP Servers | Filesystem MCP, SQLite MCP |
| 2+ External APIs | NewsAPI, Open Library API |
| 2+ Data Sources | Local PDFs/TXT + Remote APIs |

---

## 📁 File Structure

```
research-assistant/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py                    ← Entry point
│
├── config/
│   └── settings.py            ← All config & env loading
│
├── agents/
│   ├── __init__.py
│   ├── planner_agent.py       ← Breaks query into sub-tasks
│   ├── retriever_agent.py     ← Searches RAG + APIs
│   └── synthesizer_agent.py   ← Writes final answer
│
├── graph/
│   ├── __init__.py
│   ├── state.py               ← LangGraph state definition
│   └── workflow.py            ← LangGraph graph & edges
│
├── memory/
│   ├── __init__.py
│   └── memory_manager.py      ← Buffer + Summary memory
│
├── retrieval/
│   ├── __init__.py
│   ├── document_loader.py     ← Loads local docs
│   ├── chunker.py             ← Text splitting
│   └── vector_store.py        ← FAISS vector DB
│
├── mcp_tools/
│   ├── __init__.py
│   ├── filesystem_mcp.py      ← Read/write local notes
│   └── sqlite_mcp.py          ← Query local SQLite DB
│
├── api_tools/
│   ├── __init__.py
│   ├── news_api.py            ← Fetch recent news
│   └── open_library_api.py    ← Search books
│
├── data/
│   ├── local/
│   │   ├── research_notes.txt ← Sample local data
│   │   └── knowledge.db       ← SQLite DB (auto-created)
│   └── docs/
│       └── sample_paper.txt   ← Sample PDF/doc for RAG
│
└── utils/
    ├── __init__.py
    └── helpers.py             ← Shared utilities
```

---

## 🚀 Setup & Run Guide

See the Step-by-Step Guide section below in the full documentation.
